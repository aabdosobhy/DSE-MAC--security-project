from Crypto.Cipher import DES
from keys import keyMAC,keyDES
import hashlib
#from des import DesKey

blockSize = 8
blockMAC = 8
# MAC sender data processing
def sendMAC(msg):
    obj=DES.new(keyMAC, DES.MODE_ECB)
    padLen = blockMAC - (len(msg) % blockMAC)
    msg += padLen * 'X'
    # encrypt msg with keyMAC
    encryptMACkey=obj.encrypt(msg)
    # hash msg with keyMAC
    hashedMAC = hashlib.md5(encryptMACkey).hexdigest()
    return hashedMAC

class desModes():
    def __init__(self):
        # For testing purposes
        self.key = keyDES
        #self.key = DesKey(b"some key")
    
    #Split a list into sublists of size blocksize
    def splitMessage(self, plainText):
        return [plainText[k:k+blockSize] for k in range(0, len(plainText), blockSize)]
    
    def padBlock(self, block):
        padLen = blockSize - (len(block) % blockSize)
        block += padLen * chr(padLen)
        return block
    
    def stringToBits(self, text):#Convert a string into a list of bits
        array = list()
        for char in text:
            binval = self.binvalue(char, 8)#Get the char value on one byte
            array.extend([int(x) for x in list(binval)]) #Add the bits to the final list
        return array

    def bitsToString(self, array): #Recreate the string from the bit array
        res = ''.join([chr(int(y,2)) for y in 
            [''.join([str(x) for x in _bytes]) for _bytes in  self.splitMessage(array)]])   
        return res
    
    def binvalue(self, val, bitsize): #Return the binary value as a string of the given size 
        binval = bin(val)[2:] if isinstance(val, int) else bin(ord(val))[2:]
        if len(binval) > bitsize:
            raise "binary value larger than the expected size"
        while len(binval) < bitsize:
            binval = "0"+binval #Add as many 0 as needed to get the wanted size
        return binval
    
    def xor(self, t1, t2):#Apply a xor and return the resulting list
        return [x^y for x,y in zip(t1,t2)]
        
    def desECB_Enc(self, plainText):
        result=b""
        desECB=DES.new(self.key, DES.MODE_ECB)   
        textBlocks = self.splitMessage(plainText)
        for block in textBlocks:
            if len(block) < blockSize:
                block = self.padBlock(block)
            ciph=desECB.encrypt(block)
            result+=ciph
        return result

    def desECB_Dec(self, plainText):
        result = b''
        desECB=DES.new(self.key, DES.MODE_ECB)   
        textBlocks = self.splitMessage(plainText)
        for block in textBlocks:
            # if len(block) < blockSize:
            #     block = self.padBlock(block)
            dciph=desECB.decrypt(block)
            result+=dciph
        # print(desECB.decrypt(plainText))
        return result
       

    def desCBC_Enc(self, plainText, IV):
        result = list()
        desECB = DES.new(self.key, DES.MODE_ECB)        
        textBlocks = self.splitMessage(plainText)
        b_no=0
        for block in textBlocks: #Loop over all the blocks of data               
            block = self.stringToBits(block)#Convert the block in bit array
            if len(block) < blockSize:
                block = self.padBlock(block)
            if b_no == 0:
                block = self.xor(IV, block)
            else:
                block = self.xor(result[b_no-1], block)
            ciph = desECB.encrypt(block)
            result.append(ciph)
        b_no += 1
        return result

    def desCBC_Dec(self, plainText, IV):
        result = list()
        desECB=DES.new(self.key, DES.MODE_ECB)        
        textBlocks = self.splitMessage(plainText)
        for i in range (0 , len(textBlocks) ):
        #for block in textBlocks: #Loop over all the blocks of data
            block = textBlocks[i]
            if len(block) < blockSize:
                block = self.padBlock(block)
            dciph = desECB.decrypt(block)
            if i == 0:
                dciph = self.xor(IV, dciph)
            else:
                dciph = self.xor(dciph, textBlocks[i-1])
            result.append(dciph)

        return result
    
    def des_CFB_Enc(self):
        #TODO: 
        return
    
    def des_CFB_Dec(self):
        #TODO: 
        return
    
    def des_OFB_Enc(self, plainText, Nonce):
        result = list()
        nonceList = list()
        Nonce = self.stringToBits(Nonce)
        nonceList.append(Nonce)
        desECB = DES.new(self.key, DES.MODE_ECB)        
        textBlocks = self.splitMessage(plainText)
        b_no = 1
        for block in textBlocks: #Loop over all the blocks of data               
            block = self.stringToBits(block)#Convert the block in bit array
            if len(block) < blockSize:
                block = self.padBlock(block)
            ciph=desECB.encrypt(nonceList[b_no-1])
            nonceList.append(ciph)
            ciph = self.xor(ciph,block)
            result.append(ciph)
            b_no += 1
        return result

    def des_OFB_Dec(self, plainText, Nonce):
        result = list()
        nonceList = list()
        Nonce = self.stringToBits(Nonce)
        nonceList.append(Nonce)
        desECB = DES.new(self.key, DES.MODE_ECB)        
        textBlocks = self.splitMessage(plainText)
        b_no = 1
        for block in textBlocks: #Loop over all the blocks of data               
            if len(block) < blockSize:
                block = self.padBlock(block)
            dciph=desECB.decrypt(nonceList[b_no -1])
            nonceList.append(dciph)
            dciph = self.xor(dciph, block)
            result.append(dciph)
            b_no += 1
        return result
    
    
    def des_CNT_Enc(self, plainText, Count=0):
        result = list()
        desECB = DES.new(self.key, DES.MODE_ECB)        
        textBlocks = self.splitMessage(plainText)
        for block in textBlocks: #Loop over all the blocks of data               
            block = self.stringToBits(block)#Convert the block in bit array
            if len(block) < blockSize:
                block = self.padBlock(block)
            ciph=desECB.encrypt(Count)
            ciph = self.xor(ciph,block)
            result.append(ciph)
            count+=1
        return result 
    
    def des_CNT_Dec(self, plainText, Count=0):
        result = list()
        desECB = DES.new(self.key, DES.MODE_ECB)        
        textBlocks = self.splitMessage(plainText)
        for block in textBlocks: #Loop over all the blocks of data               
            if len(block) < blockSize:
                block = self.padBlock(block)
            dciph = desECB.decrypt(Count)
            dciph = self.xor(dciph, block)
            result.append(dciph)
            count+=1
        return result 

