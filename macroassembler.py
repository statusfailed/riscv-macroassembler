from typing import List

def mask(n):
    """ create an n-bit mask """
    return 2**n - 1

def slice_to_mask(s):
    # note: we follow riscv convention instead of python convention: start:stop
    # is an INCLUSIVE range.
    start, stop = s.start, s.stop
    nbits = start - stop + 1    
    return mask(nbits) << stop

def normalize_slice(s):
    # notation like self[1:2] returns a slice,
    # but self[1:2, 3:4] returns a tuple of slices.
    # To make things more consistent, we always return a *list* of slices
    if type(s) is tuple or type(s) is list:
        return list(s)
    if type(s) is int:
        return slice(s, s, None) 
    elif type(s) is slice:
        return [s]
    else:
        raise ValueError("unsupported slice key {}".format(s))


class BitVector:
    """ Length-aware bitvectors supporting concatenation, shifting, and pointwise operations.
    """
    def __init__(self, n, value=0):
        if n < 0:
            raise ValueError("Cannot create BitVector with negative length {}".format(n))

        self.length = n
        self.value  = value & mask(n)

        if value != self.value:
            raise ValueError("value {} is larger than specified bitwidth {}".format(value, n))

    # concatenation of bitvectors
    def __add__(this, that):
        n = this.length
        m = that.length
        value = (this.value << n) ^ that.value
        return BitVector(n + m, value)

    def __repr__(self):
        if self.length == 0:
            return 'BitVector(0)'
        bstr = format(self.value, '#0' + str(2 + self.length) + 'b')
        return 'BitVector({}, {})'.format(self.length, bstr)

    def __lshift__(self, amount):
        return BitVector(self.length + amount, self.value << amount)

    def __rshift__(self, amount):
        return BitVector(max(0, self.length - amount), self.value >> amount)

    def __xor__(this, that):
        if this.length != that.length:
            raise ValueError("cannot XOR bitvectors of length {} and {}".format(this.length, that.length))
        return BitVector(this.length, this.value ^ that.value)

    def __and__(this, that):
        if this.length != that.length:
            raise ValueError("cannot AND bitvectors of length {} and {}".format(this.length, that.length))
        return BitVector(this.length, this.value & that.value)

    def split(self, sizes):
        """ Split a vector into chunks of varying size
        >>> BitVector(8, 0xFF).split([2, 4, 1, 1]) == [0b11, 0b1111, 0b1, 0b1]
        """
        if sum(sizes) != self.length:
            raise ValueError("tried to split BitVector of length {}, but sizes add up to {}", self.length, sum(sizes))
        acc = self.value
        result = []
        for n in reversed(sizes):
            part = mask(n) & self.value
            acc  = self.value >> n
            result.append(BitVector(n, part))
        result.reverse()
        return result

    def __getitem__(self, key):
        raise NotImplementedError("__getitem__")

    def __setitem__(self, key, values):
        if type(values) is not list:
            values = [values]
        slices = normalize_slice(key)

        for s in slices:
            if s.step is not None:
                raise ValueError("Unknown value {} for slice {} step".format(s.step, s))
        if len(values) != len(slices):
            raise ValueError("Can't set {} values in {} locations".format(len(values), len(slices)))

        for s, v in zip(slices, values):
            if type(v) is not BitVector:
                raise ValueError("Value {} was not a BitVector".format(v))
            n = s.start - s.stop + 1
            if v.length != n:
                # TODO: better error message
                raise ValueError("Value {} length != slice {} length".format(v, s))
            m = slice_to_mask(s)
            self.value = (self.value & ~m) ^ (v.value << s.stop)


class BitSlice:
    """
    Abuse of the slice syntactic sugar: we just interpret python's slices
    directly as bit range mappings. For example:
    
    - bits[31:30]          denotes bits [31, 30]
    - bits[31:30, 10, 5:4] denotes bits [31, 30, 10, 5, 4]
    """
    def __getitem__(self, key):
        return normalize_slice(key)
bits = BitSlice()


class Instruction:
    """
    An Instruction is a mapping of parameters to (non-contiguous) bit ranges
    """
    def __init__(self, nbits, **kwargs):
        self.nbits = nbits
        self.parts = kwargs

    def validate(self):
        """
        Check that an instruction encoding is valid.
        (That is, that every bit is accounted for)
        """
        # sort ranges by start point, and check that every bit is covered
        ranges = sorted(((s.start, s.stop, name) for name, ranges in self.parts.items() for s in ranges), reverse=True)
        prev = self.nbits
        for start, stop, name in ranges:
            if start != prev - 1:
                raise ValueError("Non-contiguous bit range in part {}=bits[{}:{}]".format(name, start, stop))
            prev = stop

        if prev != 0:
            raise ValueError("Instruction did not cover bits {}:{}".format(prev-1, 0))

        return prev == 0

    def where(self, **kwargs):
        """
        Create a new instruction from this one, by setting some fields to
        constants. For example:
        
        >>> store=Instruction(bits[31:25, 11:7], src=register, base=register, width=immediate(3), opcode=constant(7, 0b0100011))
        >>> sb = store.where(width=0b0)
        """
        raise NotImplementedError("TODO")

    def encode(self, **kwargs):
        # TODO: raise error when kwargs has keys that don't appear in parts
        encoded = BitVector(self.nbits)
        for name, slices in self.parts.items():
            value_slices = [s for s in slices if s.step is None]
            # set values
            if name in kwargs:
                slice_sizes = [s.start - s.stop + 1 for s in value_slices if s.step is None]
                value = BitVector(sum(slice_sizes), kwargs[name])
                encoded[value_slices] = value.split(slice_sizes)

            # set constants
            const_slices = [s for s in slices if s.step is not None]
            const_values = [BitVector(s.start - s.stop + 1, s.step) for s in const_slices]
            key = list(slice(s.start, s.stop) for s in const_slices)
            encoded[key] = const_values
        return encoded

################################################################################
# Instructions
################################################################################

def utype(opcode):
    return Instruction(32, imm=bits[31:12], rd=bits[11:7], opcode=bits[6:0:opcode])

def itype(funct3, opcode):
    return Instruction(32, imm=bits[31:20], rs1=bits[19:15], funct3=bits[14:12:funct3], rd=bits[11:7], opcode=bits[6:0:opcode])

auipc = utype(0b0010111)
lui   = utype(0b0110111)
addi  = itype(0b000, 0b0010011)
slli  = Instruction(32,
    imm=bits[31:26:0],
    shamt=bits[25:20],
    src=bits[19:15],
    funct3=bits[14:12:0b001],
    dest=bits[11:7],
    opcode=bits[6:0:0b0010011])

# TODO: check that the "offset" value is encoded correctly!
store = Instruction(32,
    offset=bits[31:25, 11:7],
    src=bits[24:20],
    base=bits[19:15],
    width=bits[14:12], # 0b0 = byte, 0b1 = half, 0b10 = word
    opcode=bits[6:0:0b0100011])

# TODO: use the "where" method for this.
sb = Instruction(store.nbits, **{k: v for k, v in store.parts.items()})
sb.parts['width'] = bits[14:12:0]

instructions = dict(
    auipc=auipc,
    lui=lui,
    addi=addi,
    slli=slli,
    store=store,
    sb=sb,
)
