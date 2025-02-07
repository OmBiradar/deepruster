# deepruster 🦀

This is a RAG chain based rust coding assistant which can help you to write error proof rust code by directly interactin with your local rust compiler.


## Major problems faced

- Final code is not bug proof but rather just error prooof
    - Final code might be checked by some bigger model and passed back as feedback
    - Multiple answers computed at once to choose from the best by the user

- Dependencies issues
    - Never trust it to modify the `cargo.toml` file (AI knows pattern but not the exact version)
        - If you want to add a new dependency, add it through `cargo add`
        - If you want to remove a dependency, remove it through `cargo remove`
        - If you want to update a dependency, update it through `cargo update`
    - Documentation about the dependencies is not available (maybe link them while compilation)