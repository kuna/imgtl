ImgTL
=====
[![Build Status](https://travis-ci.org/imgtl/imgtl.svg?branch=master)](https://travis-ci.org/imgtl/imgtl)

### How to use
* need imgtl.cfg file. copy .imgtl.tests.cfg file to use temporarily.
* edit BASE_URL from const.py to store proper image URI.
* better to use nginx for https support & /x/ image redirect rule (you can temporary disable redirecting using <code>NONGINX = True</code> from imgtl.cfg file)

### future plan
* Tagging System (taglist, tagedit ...)
* similar image searching function (prevent uploading duplicate image)