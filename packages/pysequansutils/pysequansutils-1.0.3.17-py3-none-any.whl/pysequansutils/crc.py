"""
TERMS AND CONDITIONS OF USE OF THE SOURCE CODE

The Source Code (the “SOURCE CODE”) is the sole property of SEQUANS Communications.

USER expressly undertakes to use this SOURCE CODE for the sole and only purposes of
TESTING and DEBUGGING. USER is perfectly aware that any other use is strictly prohibited
by SEQUANS Communications and notably the distribution/sale of such SOURCE CODE is
strictly prohibited by SEQUANS Communications. CONSIDERING THAT THE SOURCE CODE IS
PROVIDED BY COURTESY OF SEQUANS COMMUNICATIONS AND AT NO CHARGE, USER ACKNOWLEDGES
AND ACCEPTS THAT SUCH SOURCE CODE IS PROVIDED “AS IS” WITH NO ASSOCIATED DOCUMENTATION,
NO SUPPORT OR MAINTENANCE OF ANY KIND, NO WARRANTIES, EXPRESS OR IMPLIED, WHATSOEVER.
USER ACKNOWLEDGES THAT IN NO EVENT SHALL SEQUANS COMMUNICATIONS BE LIABLE FOR ANY CLAIM,
DAMAGES OR LOSS, DIRECT, INCIDENTAL, INDIRECT, SPECIAL OR CONSEQUENTIAL - ARISING FROM,
OUT OF OR IN CONNECTION WITH ANY USE OF THE SOURCE CODE. No Intellectual Property or
licensing rights shall be assigned to USER, under any form or for any purpose whatsoever,
with respect to the SOURCE CODE. Any modification, whatsoever, of the SOURCE CODE is
strictly prohibited WITHOUT PRIOR WRITTEN CONSENT OF SEQUANS Communications.

THE USE OF THE SOURCE CODE IS SUBJECT TO THE PRIOR ACCEPTANCE OF THESE TERMS AND CONDITIONS.
"""
from . import codec

# -------------------------------------------------// Fletcher /_________________________________
def fletcher32 (data, endian=codec.BIG_ENDIAN):
	l = len(data)

	index = 0
	s1 = s2 = 0xFFFF
	while l > 1:
		qty = 720 if l > 720 else (l & ~1)
		l -= qty

		qty += index
		while index < qty:
			word = codec.decode.u16(data[index:index+2], endian)
			s1 += word
			s2 += s1

			index += 2

		s1 = (s1 & 0xFFFF) + (s1 >> 16)
		s2 = (s2 & 0xFFFF) + (s2 >> 16)

	if (l & 1):
		s1 += data[index] << 8
		s2 += s1

		s1 = (s1 & 0xFFFF) + (s1 >> 16)
		s2 = (s2 & 0xFFFF) + (s2 >> 16)

	s1 = (s1 & 0xFFFF) + (s1 >> 16)
	s2 = (s2 & 0xFFFF) + (s2 >> 16)

	return (s2 << 16) | s1

