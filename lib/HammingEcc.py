#!/usr/bin/python3

import sys 


class HammingEcc:

  #-----------------------------------------------------------------  
  #  Constructor
  #-----------------------------------------------------------------  
  def __init__(self):
    pass

  #-----------------------------------------------------------------  
  #  Convert a bit array to a byte array
  #  bits[0] and bytes[0] are LSB
  #  Returns byte array
  #-----------------------------------------------------------------  
  def bitsToBytes(self, bits, bigEndian=False):
    bytes = []
    byteCount = (len(bits) + 7) // 8

    for byteNum in range(byteCount):
      byteValue = 0
      for bit in range(8):
        bitNum = byteNum * 8 + bit
        if bits[bitNum] == 1:
          if bigEndian:
            byteValue = byteValue | (1 << (7-bit))
          else:
            byteValue = byteValue | (1 << bit)
      bytes.append(byteValue)

    return bytes

  #-----------------------------------------------------------------  
  #  Convert a byte array to a bit array
  #  bits[0] and bytes[0] are LSB
  #  Returns bit array
  #-----------------------------------------------------------------  
  def bytesToBits(self, bytes, bigEndian=False):
    bits = []
    for byte in bytes:
      for bit in range(8):
        if bigEndian:
          if (byte & (1<<(7-bit))) > 0:
            bitVal = 1 
          else:
            bitVal = 0
        else:
          if (byte & (1<<bit)) > 0:
            bitVal = 1 
          else:
            bitVal = 0

        bits.append(bitVal)

    return bits 

  #-----------------------------------------------------------------  
  #  Encode bits
  #-----------------------------------------------------------------  
  def encodeBits(self, inputBits):
    outputBits = []
    partyBitCount = 0
    pos = 0
    position = 0
    while len(inputBits) > ((1 << pos) - (pos + 1)):
      partyBitCount = partyBitCount + 1
      pos = pos + 1
  
    parityPos = 0
    nonPartyPos = 0
    i = 0
    while i < (partyBitCount + len(inputBits)):
      if i == ((1<<parityPos)-1):
        outputBits.append(0)
        parityPos = parityPos + 1
      else:
        outputBits.append(inputBits[nonPartyPos])
        nonPartyPos = nonPartyPos + 1
      i = i + 1
 
    i = 0
    while i < partyBitCount:
      position = 1 << i
      s = 0
      count = 0
      s = position - 1
      while s < (partyBitCount + len(inputBits)):
        j = s
        while j < (s + position):
          if len(outputBits) > j and outputBits[j] == 1:
            count = count + 1
          j = j + 1
        s = s + 2*position

      if (count % 2) == 0: 
        outputBits[position-1] = 0
      else:
        outputBits[position-1] = 1
      i = i + 1

    extraParity = 0
    for bit in outputBits:
      extraParity = extraParity | bit
    outputBits.append(extraParity)

    return outputBits


  #-----------------------------------------------------------------  
  #  Decode bits
  #-----------------------------------------------------------------  
  def decodeBits(self, inputBits):
    outputBits = []
    ss = 0
    error = 0
    parityBitsRemoved = 0
    workBits = inputBits
    extraParity = workBits[len(workBits)-1]

    workBits = workBits[0:len(workBits)-1]

    length = len(workBits) 
    parityCount = 0

    pos = 0
    while (len(inputBits) - parityCount) > ((1<<pos) - (pos+1)):
      parityCount = parityCount + 1
      pos = pos + 1

    # Check whether there are any errors
    i = 0
    while i < parityCount:
      count = 0
      position = 1 << i
      ss = position-1
      while ss < length:
        sss = ss

        while sss < (ss + position):
          if sss < len(workBits) and workBits[sss] == 1:
            count = count + 1
          sss = sss + 1
    
        ss = ss + 2*position

      if (count % 2) != 0:
        error = error + position
      i = i + 1
    
    if error != 0:
      if workBits[error-1] == 1:
        workBits[error-1] = 0
      else:
        workBits[error-1] = 1

      i = 0
      while i < length:
        if i == ((1 << parityBitsRemoved)-1):
          parityBitsRemoved = parityBitsRemoved + 1
        else:
          if len(workBits) > i:
            outputBits.append(workBits[i])
          else:
            outputBits.append(0)
        i = i + 1

    else:
      i = 0
      while i < length:
        if i == ((1 << parityBitsRemoved)-1):
          parityBitsRemoved = parityBitsRemoved + 1
        else:
          outputBits.append(workBits[i])
        i = i + 1

    parity = 0
    for bit in outputBits:
      parity = parity | bit
    
    if parity != extraParity:
      return []
 
    return outputBits



#-----------------------------------------------------------------  
#  Main 
#-----------------------------------------------------------------  
def main(args):
  ecc = HammingEcc()
  bits = [1, 0, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 0, 
          1, 0, 0, 0, 1, 0, 1, 0, 
          0, 1, 0, 1, 0, 0, 0, 1, 
          0, 0, 0, 0, 0, 1, 0, 0, 
          0, 0, 0, 0, 0, 1, 1, 0, 
          1, 0, 1, 0, 0, 0, 0, 0, 
          1, 1, 0, 0, 1, 1, 1, 0, 
          0, 0, 0, 0, 0, 0, 0, 0, 
          0, 0, 0, 0, 0, 0, 0, 0  ]

  bytes = ecc.bitsToBytes(bits)
  recovered_bits = ecc.bytesToBits(bytes)
  encoded_bits = ecc.encodeBits(bits)
  decoded_bits = ecc.decodeBits(encoded_bits)
  decoded_bytes = ecc.bitsToBytes(decoded_bits)

  print(f"bits = {bits}")
  print(f"bytes = {bytes}")
  print(f"recovered bytes = {recovered_bits}")
  print(f"encoded bits = {encoded_bits}")
  print(f"decoded bits = {decoded_bits}")
  print(f"decoded bytes = {decoded_bytes}") 

if __name__ == '__main__':
  main(sys.argv[1:])

