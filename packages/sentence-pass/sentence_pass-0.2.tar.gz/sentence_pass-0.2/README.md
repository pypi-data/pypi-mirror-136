Sentence to password
This package contains class Password, with one method `generate_password`.
This method takes one sentence and make it a password by adding number and special character into it

Example:
```{python}
    >>> from sen_pass.password_generator import Password
    >>> pw = Password(8, "Sad Autumn Girl")
    >>> print(pw.generate_password())
    S@d@utumnGirl291
    >>> print(pw.generate_password())
    S@d@utumnGirl291
    >>> print(pw.generate_password())
    $adAutumnGirl291
```
