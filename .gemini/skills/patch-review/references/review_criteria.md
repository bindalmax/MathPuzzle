# Industry Standard Code Review Criteria

When performing a code review, evaluate the changes against the following dimensions:

## 1. Logic and Correctness
- **Functionality**: Does the code do what it's supposed to do?
- **Edge Cases**: Are boundary conditions, null/empty inputs, and error states handled?
- **Complexity**: Is the implementation unnecessarily complex? Can it be simplified?

## 2. Design and Architecture
- **SOLID Principles**: Does the code follow Single Responsibility, Open/Closed, etc.?
- **DRY (Don't Repeat Yourself)**: Is there duplicated logic that should be abstracted?
- **Coupling**: Are components too tightly coupled?
- **Patterns**: Are appropriate design patterns used (Factory, Strategy, etc.)?

## 3. Security
- **Input Validation**: Is all user input sanitized/validated?
- **Secrets**: Are any API keys, passwords, or PII exposed or committed?
- **Injection**: Are there risks of SQL, Command, or XSS injections?
- **Dependencies**: Are new dependencies safe and necessary?

## 4. Performance and Efficiency
- **Resource Usage**: Are there obvious memory leaks, unnecessary DB queries, or heavy loops?
- **Scalability**: Will this code work efficiently as data grows?
- **Async/Sync**: Are blocking operations used correctly?

## 5. Testing and Validation
- **Coverage**: Are there new tests for new functionality?
- **Test Quality**: Do tests actually verify behavior or just exercise the code?
- **Regressions**: Is it likely this change breaks existing functionality?

## 6. Readability and Style
- **Naming**: Are variables, functions, and classes named descriptively?
- **Documentation**: Are complex blocks of logic commented? Is the public API documented?
- **Conventions**: Does it follow the project's established coding style (PEP8, Airbnb, etc.)?
- **Formatting**: Is the code formatted consistently?

## 7. Maintainability
- **Technical Debt**: Does this change introduce "hacks" that will need to be fixed later?
- **Future-proofing**: Is the code written in a way that is easy to extend or modify?
