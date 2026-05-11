# System-shipped expressions

This directory is intentionally empty in the current iteration. It exists so the asset-root
scan for `expressions` always finds the system-shipped root, even when no built-in expressions
have been shipped yet.

When new expressions are placed here they become available to every user of MPFB.

## User-vs-system precedence

Expressions are discovered across the four standard MPFB asset roots
(`mpfb_data`, `mh_user_data`, `user_data`, `second_root`). When the same library-relative path
is present in more than one root, the highest-priority root wins — matching the same rule used
for poses. User-saved expressions therefore override system-shipped ones with the same name.
