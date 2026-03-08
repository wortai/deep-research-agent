# WORT Engine Project Rules 

## 1. Naming 
- **Classes**: *use PascalCase* (e.g., `ResearchAgent`)
- **Files & Folders & Methods & Variables**: for folders and files *snake_case* (e.g., `research_agent.py`, `data_processing/`)
- **Constants**: `UPPER_CASE` (e.g., `MAX_RETRIES`)
- **Method or Class Name**: Only use name that explains about class , method or folder. **Don't use** anything like , processor ,manager , hander , worker , unless there's no other option. Be Specific about your class or method names (should indicate what class or method does).
## 2. Code Structure
- **One Class Per File**: Each file must contain exactly one main class.
- **Encapsulation**: Wrap logic in classes. Avoid top-level functions unless they are simple utilities.
- **Modularity**: Break complex logic into smaller, reusable components.

## 3. Folder Structure
- **Task-Based Grouping**: If a task requires multiple files, create a dedicated folder for it.
- **Module Wrapping**: Wrap related modules in a folder to keep the root directory clean.

## 4. Documentation
- **Docstrings**: Mandatory for all classes and most methods.
- **Content**: Concisely explain:
    - **Purpose**: What the class/method does.
    - **Inputs**: Parameters and their types.
    - **Outputs**: Return values and their types.
    - **ConciseExplanation**: Explain what this method or class , dependent on and how building over it for Ex- if class X does research and Class Y review it , then while writing comment for Class Y "explain Class Y pass params (x1.....xn) to Class X to get this output (y1...yn) that used in this... way
- **eStyl**: Avoid generic comments like "doing research". Be specific about the action.

## 5. Clean Code Practices
- **No Unnecessary IO**: Remove `print` statements that are not essential for logging or final output.
- **Dead Code**: Only declare methods that are currently used or you sure , will be used , **immediate** future use.
- **Comments**: Use docstrings for documentation. Avoid inline comments (`#`) unless very  necessary to explain complex, non-obvious logic and Inline comments should be 1 Liners .
