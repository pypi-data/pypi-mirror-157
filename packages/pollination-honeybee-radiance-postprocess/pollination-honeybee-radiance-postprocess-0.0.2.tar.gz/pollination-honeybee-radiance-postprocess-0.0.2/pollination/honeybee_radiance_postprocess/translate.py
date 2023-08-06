from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class BinaryToNpy(Function):
    """Convert binary Radiance matrix file to NumPy file."""
    matrix_file = Inputs.file(
        description='Path to binary Radiance matrix file.',
        path='input.ill', extensions=['ill', 'dc']
    )

    conversion = Inputs.str(
        description='Conversion as a string which will be passed to rmtxop -c option.',
        default=''
    )

    @command
    def binary_to_npy(self):
        return 'honeybee-radiance-postprocess translate binary-to-npy ' \
            '{{self.matrix_file}} --conversion "{{self.conversion}}" --name output'

    output_file = Outputs.file(
        description='Output as a npy file.', path='output.npy'
        )
