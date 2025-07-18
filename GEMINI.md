# Gemini Project: nlpi

This document outlines the vision, architecture, and development guidelines for the `nlpi` project. As the Gemini agent, your primary role is to assist in building and maintaining this project according to these guidelines.

## Project Objective

`nlpi` is a Natural Language Programming Interface (NLPI) designed to function as an MCP (Mission Control Plane) server. The target users are developers who may not have deep expertise in DevOps or cloud infrastructure deployment.

The core purpose of `nlpi` is to allow a developer to describe their deployment goals in plain English. The system, powered by an LLM, will interpret these requests and guide the user through the necessary steps to correctly deploy their software. This includes a wide range of tasks, from generating a `Dockerfile` and pushing a container image to a registry, to provisioning cloud infrastructure like a VPC in AWS. The ultimate goal is to simplify the deployment process, making it accessible and intuitive.

## Architectural Constraints & Key Technologies

A critical requirement for this project is the adoption of **`fastmcp2.0`**. You must replace any existing MCP-related dependencies with `fastmcp2.0` from the following repository: [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp).

When implementing new features or modifying existing code, ensure that all interactions with MCP functionality are routed through this specific library.

## Development Guidelines

Your development process should adhere to the following professional standards:

1.  **Incremental Changes:** Implement changes in small, logical, and atomic commits. This makes code review easier and helps isolate potential issues.
2.  **Commit Frequency:** Make commits after implementing new features, fixing bugs, or completing any logical unit of work. As a general guideline, consider creating a commit after changes that are roughly 50 lines of code.
3.  **High-Quality Code:**
    *   **Documentation:** All new functions, classes, and modules should have clear and concise docstrings explaining their purpose, arguments, and return values.
    *   **Comments:** Use inline comments to clarify complex or non-obvious logic. Focus on the *why*, not the *what*.
    *   **Design:** Strive for a clean, professional, and maintainable codebase. Follow established software design patterns where appropriate.
4.  **Industry Best Practices:** Adhere to Python community standards (e.g., PEP 8) and modern development practices.
5.  **Review-Oriented Workflow:** After making a set of changes, present them for review. Explain the changes made and their purpose.
