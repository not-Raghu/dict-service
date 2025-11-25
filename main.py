import sys
import ctypes
import ctypes.util

#to load objc
def find_and_load(name):
    return ctypes.cdll.LoadLibrary(ctypes.util.find_library(name))


objc = find_and_load('objc')
objc.objc_getClass.restype = ctypes.c_void_p
objc.sel_registerName.restype = ctypes.c_void_p
objc.objc_msgSend.restype = ctypes.c_void_p
objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

Foundation = find_and_load('Foundation')
CoreFoundation = find_and_load('CoreFoundation')
CoreServices = find_and_load('CoreServices')

NSString = objc.objc_getClass(b'NSString')
NSAutoreleasePool = objc.objc_getClass(b'NSAutoreleasePool')
Boolean = ctypes.c_uint8
CFIndex = ctypes.c_long
CFStringRef = ctypes.c_void_p
CFStringEncoding = ctypes.c_uint32
CFStringEncodingUTF8 = 0x08000100

CFStringCreateWithBytes = Foundation.CFStringCreateWithBytes
CFStringCreateWithBytes.restype = CFStringRef
CFStringCreateWithBytes.argtypes = [
    ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), CFIndex,
    CFStringEncoding, Boolean]


class CFRange(ctypes.Structure):
    _fields_ = [('location', CFIndex), ('length', CFIndex)]


DCSCopyTextDefinition = CoreServices.DCSCopyTextDefinition
DCSCopyTextDefinition.restype = CFStringRef
DCSCopyTextDefinition.argtypes = (ctypes.c_void_p, CFStringRef, CFRange)


def sel_name(name):
    return objc.sel_registerName(name.encode('ascii'))

#look up from dict service
def lookup_word(word):
    word_bytes = word.encode('utf-8')
    word_cfstring = CFStringCreateWithBytes(
        None, word_bytes, len(word_bytes), CFStringEncodingUTF8, False)
    definition_nsstring = DCSCopyTextDefinition(
        None, word_cfstring, CFRange(0, len(word_bytes)))
    definition = ctypes.c_char_p(objc.objc_msgSend(
        definition_nsstring, sel_name('UTF8String')))
    if definition.value:
        return definition.value.decode('utf-8')

#output from dict service
def report(text):
    sys.stdout.write(u'%s\n' % text)
    sys.exit(0)

#abort if not found
def abort(text):
    sys.stderr.write(u'%s\n' % text)
    sys.exit(1)

def main():
    if(len(sys.argv)<1):
        print("No argument provided. Usage: python3 main.py <word>")
        return
    word = sys.argv[1]
    definition = lookup_word(word)
    if definition is None:
        abort(u'Definition not found for "%s"' % word)
    else:
        report(definition)



main()
