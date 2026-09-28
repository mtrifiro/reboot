import aiofiles
import aiofiles.os
import os
import re
import tempfile
import unittest
from tests.reboot.cli.generate.tests_helper import (
    DEFAULT_API_DIR,
    RbtGenerateBaseTestCase,
)

# Models shared between API files: an error type every API may raise,
# and a plain model that API states hold as a field. The file defines
# no `api` of its own.
SHARED_MODELS = """
from reboot.api import Field, Model


class NotFoundError(Model):
    message: str = Field(tag=1)


class Money(Model):
    cents: int = Field(tag=1)
"""

# A helper file with no `Model`s and no `api`, which must be ignored.
SHARED_HELPER = """
CURRENCY = "USD"
"""


def api_file(type_name: str) -> str:
    return f"""
from reboot.api import API, Field, Methods, Model, Reader, Type, Writer
from shared.errors import Money, NotFoundError
from shared.helper import CURRENCY


class {type_name}State(Model):
    total: Money = Field(tag=1)


api = API(
    {type_name}=Type(
        state={type_name}State,
        methods=Methods(
            create=Writer(
                request=None,
                response=None,
                factory=True,
                mcp=None,
            ),
            total=Reader(
                request=None,
                response=Money,
                errors=[NotFoundError],
                mcp=None,
            ),
        ),
    ),
)
"""


class RbtGenerateTestCase(RbtGenerateBaseTestCase):

    async def test_models_shared_between_pydantic_api_files(self):
        with tempfile.TemporaryDirectory() as root:
            api_directory = os.path.join(root, DEFAULT_API_DIR)
            files = {
                'shared/errors.py': SHARED_MODELS,
                'shared/helper.py': SHARED_HELPER,
                'bank/v1/bank.py': api_file('Bank'),
                'store/v1/store.py': api_file('Store'),
            }
            for path, content in files.items():
                path = os.path.join(api_directory, path)
                await aiofiles.os.makedirs(
                    os.path.dirname(path),
                    exist_ok=True,
                )
                async with aiofiles.open(path, 'w') as file:
                    await file.write(content)

            await self.run_generate(
                '--python=backend_out',
                '--web=web_out',
                '--react=react_out',
                DEFAULT_API_DIR,
                working_directory=root,
            )

            # The generated Python code names each error by its module
            # and class, e.g., `shared.errors.NotFoundError`, so it
            # must import the module defining a shared error. (Under
            # Bazel every module shares the top-level `tests` package,
            # which the `_pb2` imports bind, hiding a missing import.)
            for api_rbt in ['bank/v1/bank_rbt.py', 'store/v1/store_rbt.py']:
                async with aiofiles.open(
                    os.path.join(root, 'backend_out', api_rbt)
                ) as file:
                    python = await file.read()
                self.assertIn('shared.errors.NotFoundError', python)
                self.assertIn('\nimport shared.errors\n', python)
                # A file without any `Model` is never imported.
                self.assertNotIn('shared.helper', python)

            for output_directory in ['web_out', 'react_out']:
                output_directory = os.path.join(root, output_directory)

                # The file defining the shared models gets Zod types
                # of its own, which the API files' Zod types import.
                await self.expect_files(
                    directory=os.path.join(output_directory, 'shared'),
                    expected_files=['errors_rbt_types.ts'],
                )
                # A file with neither an `api` nor any `Model` gets
                # nothing.
                await self.expect_no_files(
                    directory=os.path.join(output_directory, 'shared'),
                    not_expected_files=['helper_rbt_types.ts'],
                )

                async with aiofiles.open(
                    os.path.join(
                        output_directory,
                        'shared',
                        'errors_rbt_types.ts',
                    )
                ) as file:
                    shared_zod = await file.read()

                # `NotFoundError` is an error of the API files'
                # methods, so it carries the `type` discriminator;
                # `Money` is not, so it doesn't.
                self.assertIn('export const NotFoundErrorSchema', shared_zod)
                self.assertIn(
                    'type: z.literal("NotFoundError")',
                    shared_zod,
                )
                self.assertIn('export const MoneySchema', shared_zod)
                self.assertNotIn('z.literal("Money")', shared_zod)

                # Every relative import in the API files' Zod types
                # resolves to a generated file.
                for api_zod in [
                    'bank/v1/bank_rbt_types.ts',
                    'store/v1/store_rbt_types.ts',
                ]:
                    api_zod = os.path.join(output_directory, api_zod)
                    async with aiofiles.open(api_zod) as file:
                        imports = re.findall(
                            r'from "(\.\.?/[^"]+)";',
                            await file.read(),
                        )
                    self.assertIn('../../shared/errors_rbt_types', imports)
                    for relative_import in imports:
                        imported = os.path.normpath(
                            os.path.join(
                                os.path.dirname(api_zod),
                                relative_import,
                            )
                        ) + '.ts'
                        self.assertTrue(
                            await aiofiles.os.path.isfile(imported),
                            f"'{api_zod}' imports missing '{imported}'",
                        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
