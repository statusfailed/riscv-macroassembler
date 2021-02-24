################################################################################
# This script checks every instruction defined in macroassembler.py succeeds   #
# when calling its `validate` method. This is basically a sanity check that    #
# the encoding doesn't leave any undefined bits, or define a bit as two        #
# different things.                                                            #
################################################################################

from macroassembler import instructions

def validate_instructions(instructions):
    success = True
    for name, instruction in instructions.items():
        try:
            valid = instruction.validate()
        except ValueError as e:
            print(name, 'INVALID', str(e), sep='\t')
            success = False
        else:
            print(name, 'VALID', sep='\t')
    print('-------------------------------')
    print('All instructions valid' if success else 'error')

if __name__ == "__main__":
    validate_instructions(instructions)
