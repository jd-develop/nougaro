# Changelog
This file is updated nearly every commit and copied to GH release changelog. Its content is deleted each new version.

## 0.16.0 beta
* Better error messages
* Add `import ... as ...`
* Change `export ...` to `export (node) as ...`
* Switch to semantic versioning
* Update `reverse` builtin function (fix error message + can now take strings as argument)
* Add `var ... ++` and `var ... --`
* Change `export id (as id)` to `export (any expr) as id`
* Add `__args__` to have access to CLI args (except in Nebraska)
