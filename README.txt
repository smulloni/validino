==========
 Validino
==========

Validino is a simple validation/data-conversion library for Python
with a functional flavor.  

Validino is very much indebted to Ian Bicking's ``FormEncode``
(http://formencode.org/); indeed, it is essentially a rewrite of a
limited subset of it, with a functional rather than declarative
syntax.


Example
=======

Here is a simple example of using a validino validation schema::

  import validino as V
  validators=dict(
    url=(V.not_empty("Please enter a URL"), 
         V.url("Please enter a valid URL")),
    name=(V.not_empty("Please enter your name"), 
          V.clamp_length(max=40, msg="That name is too long")),
    age=V.either(V.empty(), 
                 V.compose(V.integer("Please enter a number"),
                           V.clamp(min=0, max=130, 
                                   msg="Yeah right"))),
    gender=V.either(V.empty(), V.belongs(('male', 'female'))),
    email=V.email(msg="Please enter a valid email address"),
    email_confirm=V.not_empty("Please confirm your email address"),
    location=V.either(V.empty(), 
                      V.clamp_length(max=30, 
                                     msg="That location is too long")),
    comment=(V.not_empty(), 
             V.clamp_length(max=400, 
                            msg="That comment is too long")))

  validators[('email', 'email_confirm')]=V.fields_equal(
     msg="Email address do not match", 
     field='email_confirm')
  myschema=V.Schema(validators)

  data=dict(url="http://example.com/",
            name="Jacob",
            email="smull@example.com",
            location="New York",
            comment="Nice legs")
  try:
    converted=s(data)
  except V.Invalid, vin:
    errors=vin.unpack_errors()
    handleErrors(errors)
  else:
    goToTown(converted)



  



















