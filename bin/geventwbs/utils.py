from __future__ import absolute_import, division, print_function
import sys
import subprocess

UTF8_ACCEPT = 0
UTF8_REJECT = 1
PY3 = sys.version_info[0] == 3
PY2 = sys.version_info[0] == 2


# DFA transitions
UTF8VALIDATOR_DFA = (
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 00..1f
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 20..3f
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 40..5f
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 60..7f
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,  # 80..9f
    7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,  # a0..bf
    8, 8, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,  # c0..df
    0xa, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x4, 0x3, 0x3,  # e0..ef
    0xb, 0x6, 0x6, 0x6, 0x5, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8,  # f0..ff
    0x0, 0x1, 0x2, 0x3, 0x5, 0x8, 0x7, 0x1, 0x1, 0x1, 0x4, 0x6, 0x1, 0x1, 0x1, 0x1,  # s0..s0
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1,  # s1..s2
    1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1,  # s3..s4
    1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1,  # s5..s6
    1, 3, 1, 1, 1, 1, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # s7..s8
)


if PY2:
    bytes = str
    text_type = unicode
    string_types = basestring
    range_type = xrange
    iteritems = lambda x: x.iteritems()
    # b = lambda x: x

    UTF8VALIDATOR_DFA_S = bytes(UTF8VALIDATOR_DFA)

    class Utf8Validator(object):
        """
        Incremental UTF-8 validator with constant memory consumption (minimal state).

        Implements the algorithm "Flexible and Economical UTF-8 Decoder" by
        Bjoern Hoehrmann (http://bjoern.hoehrmann.de/utf-8/decoder/dfa/).
        """

        def __init__(self):
            self.reset()

        def decode(self, b):
            """
            Eat one UTF-8 octet, and validate on the fly.

            Returns ``UTF8_ACCEPT`` when enough octets have been consumed, in which case
            ``self.codepoint`` contains the decoded Unicode code point.

            Returns ``UTF8_REJECT`` when invalid UTF-8 was encountered.

            Returns some other positive integer when more octets need to be eaten.
            """
            tt = UTF8VALIDATOR_DFA_S[b]
            if self.state != UTF8_ACCEPT:
                self.codepoint = (b & 0x3f) | (self.codepoint << 6)
            else:
                self.codepoint = (0xff >> tt) & b
            self.state = UTF8VALIDATOR_DFA_S[256 + self.state * 16 + tt]
            return self.state

        def reset(self):
            """
            Reset validator to start new incremental UTF-8 decode/validation.
            """
            self.state = UTF8_ACCEPT  # the empty string is valid UTF8
            self.codepoint = 0
            self.i = 0

        def validate(self, ba):
            """
            Incrementally validate a chunk of bytes provided as string.

            Will return a quad ``(valid?, endsOnCodePoint?, currentIndex, totalIndex)``.

            As soon as an octet is encountered which renders the octet sequence
            invalid, a quad with ``valid? == False`` is returned. ``currentIndex`` returns
            the index within the currently consumed chunk, and ``totalIndex`` the
            index within the total consumed sequence that was the point of bail out.
            When ``valid? == True``, currentIndex will be ``len(ba)`` and ``totalIndex`` the
            total amount of consumed bytes.
            """
            #
            # The code here is written for optimal JITting in PyPy, not for best
            # readability by your grandma or particular elegance. Do NOT touch!
            #
            l = len(ba)
            i = 0
            state = self.state
            while i < l:
                # optimized version of decode(), since we are not interested in actual code points
                state = UTF8VALIDATOR_DFA_S[256 + (state << 4) + UTF8VALIDATOR_DFA_S[ba[i]]]
                if state == UTF8_REJECT:
                    self.state = state
                    self.i += i
                    return False, False, i, self.i
                i += 1
            self.state = state
            self.i += l
            return True, state == UTF8_ACCEPT, l, self.i
else:
    text_type = str
    string_types = str,
    range_type = range
    iteritems = lambda x: iter(x.items())
    # b = lambda x: codecs.latin_1_encode(x)[0]
    # convert DFA table to string (performance)
    UTF8VALIDATOR_DFA_S = ''.join([chr(c) for c in UTF8VALIDATOR_DFA])

    class Utf8Validator(object):
        """
        Incremental UTF-8 validator with constant memory consumption (minimal state).

        Implements the algorithm "Flexible and Economical UTF-8 Decoder" by
        Bjoern Hoehrmann (http://bjoern.hoehrmann.de/utf-8/decoder/dfa/).
        """

        def __init__(self):
            self.reset()

        def decode(self, b):
            """
            Eat one UTF-8 octet, and validate on the fly.

            Returns ``UTF8_ACCEPT`` when enough octets have been consumed, in which case
            ``self.codepoint`` contains the decoded Unicode code point.

            Returns ``UTF8_REJECT`` when invalid UTF-8 was encountered.

            Returns some other positive integer when more octets need to be eaten.
            """
            tt = ord(UTF8VALIDATOR_DFA_S[b])
            if self.state != UTF8_ACCEPT:
                self.codepoint = (b & 0x3f) | (self.codepoint << 6)
            else:
                self.codepoint = (0xff >> tt) & b
            self.state = ord(UTF8VALIDATOR_DFA_S[256 + self.state * 16 + tt])
            return self.state

        def reset(self):
            """
            Reset validator to start new incremental UTF-8 decode/validation.
            """
            self.state = UTF8_ACCEPT  # the empty string is valid UTF8
            self.codepoint = 0
            self.i = 0

        def validate(self, ba):
            """
            Incrementally validate a chunk of bytes provided as string.

            Will return a quad ``(valid?, endsOnCodePoint?, currentIndex, totalIndex)``.

            As soon as an octet is encountered which renders the octet sequence
            invalid, a quad with ``valid? == False`` is returned. ``currentIndex`` returns
            the index within the currently consumed chunk, and ``totalIndex`` the
            index within the total consumed sequence that was the point of bail out.
            When ``valid? == True``, currentIndex will be ``len(ba)`` and ``totalIndex`` the
            total amount of consumed bytes.
            """
            #
            # The code here is written for optimal JITting in PyPy, not for best
            # readability by your grandma or particular elegance. Do NOT touch!
            #
            l = len(ba)
            i = 0
            state = self.state
            while i < l:
                # optimized version of decode(), since we are not interested in actual code points
                try:
                    state = ord(UTF8VALIDATOR_DFA_S[256 + (state << 4) + ord(UTF8VALIDATOR_DFA_S[ba[i]])])
                except:
                    import ipdb; ipdb.set_trace() 
                if state == UTF8_REJECT:
                    self.state = state
                    self.i += i
                    return False, False, i, self.i
                i += 1
            self.state = state
            self.i += l
            return True, state == UTF8_ACCEPT, l, self.i
