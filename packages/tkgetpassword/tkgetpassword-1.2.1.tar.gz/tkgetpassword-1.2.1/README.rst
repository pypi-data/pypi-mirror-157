Functions to create password entries:
=====================================

askcreatepassword, askoldpassword, askchangepassword

1- **askcreatepassword**\ (…) Use on create a new password, return (str:
a new password)

2- **askoldpassword**\ (…) Use on get old password and check with
functions Sha’s (HASH), return (str: old password)

3- **askchangepassword**\ (…) Use on change old password, return (str:
old password, str: new passwod)

Creation password:
==================

::

   from tkinter import Tk
   import tkgetpassword as tkpassw

   root = Tk()

   newpass = tkpassw.askcreatepassword(root, minlenght=12)

   root.mainloop()

Auth password:
==============

::

   import hashlib

   thehash = hashlib.sha256( newpass.encode() ).hexdigest()

   oldpass = tkpassw.askoldpassword(root, thehash)

Change password
===============

::

   oldpass , newpass = tkpassw.askchangepassword(root, hashed)
           
   if not (oldpass and newpass):
         print("form change password is canceled")

use help(module) :
==================

::

   help(tkgetpassword)

Options \**kw use:
==================

::

       -title: optional title str
       -message: optional message str
       
       -font1: optional (font of label passwords)
       -font2: optional (font of passwords)
       
       -showchar: default is "*"
       
       -minlenght: default 0 (no limits)
       -maxlenght: default 0 (no limits)
       
       -asserthash: a string hash to authenticate (example:
               a representation hash: hashlib.new("sha256", bytesPassword).hexdigest()
               ignored by askcreatepassword(...) function
       -namesha: default used is "sha256",
               used on hashlib.new(namesha, passw).hexdisgest() method
               
       -textbutton: default is a tuple ("Ok", "Cancel")
       -stylebutton: default is "TButton"

\**\* Changes, updates \**\*
============================

::

    release 1.1.1: added variable "version"
