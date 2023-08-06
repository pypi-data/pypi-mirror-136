from .transformers import get_transformer_class
from .fs import load_from_yaml
from .models.ir import IR

FILENAME: str = "types.yaml"


class TypeBuf:
    def __init__(self, filename: str, languages: tuple[str, ...], quiet: bool = False):
        self.filename: str = filename
        self.languages = languages
        self.quiet = quiet
        self.intermediate_representation: IR = IR(**load_from_yaml(self.filename))

    def __dict__(self) -> dict:
        return {
            'filename': self.filename,
            'languages': self.languages,
            'IR': self.intermediate_representation.dict(),
        }

    def compile(self) -> None:
        """
        Generates the output str
        :return:
        """
        if self.intermediate_representation.typedef_c < 1:
            return
        if len(self.languages) < 1:
            return

        # Store each Transformer object after we have successfully generated
        # it's output buffer, then we'll write them all at the end
        transformers = []

        # Loop through the langs specified
        for lang in self.languages:
            transformer_class = get_transformer_class(lang)

            # For each new Typedef in the definitions file
            for typedef in self.intermediate_representation.typedefs:
                transformer = transformer_class(typedef)
                transformer.generate_filename()
                for fn in transformer.method_order:
                    transformer.output_buf += fn()
                transformers.append(transformer)

        # Loop through each Transformer we prepared and start writing
        # the generated code out to files.
        # We save this step until the end so that if one fails, they all
        # fail in a "transactional" way
        for tr in transformers:
            if not self.quiet:
                print(f'>> writing {tr.output_file}..')
            tr.write_buf()
