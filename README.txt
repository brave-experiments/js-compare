usage: js-compare [-h] [-o OUTPUT] [--threshold THRESHOLD]
                  [-t {all,loose,Identifier,PrivateName,Literals,Programs,Functi
ons,Statements,Declarations,Misc,Expressions,Template Literals,Patterns,Classes,
Modules} [{all,loose,Identifier,PrivateName,Literals,Programs,Functions,Statemen
ts,Declarations,Misc,Expressions,Template Literals,Patterns,Classes,Modules} ...
]]
                  [-w WORKSPACE]
                  file1 file2

Compares JavaScript code units, based on their AST

positional arguments:
  file1                 Path to first JavaScript code unit to compare.
  file2                 Path to second JavaScript code unit to compare.

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Path to write comparison results to. Use '-' to write
                        results to STDOUT. (default: -)
  --threshold THRESHOLD
                        The minimum weight for a subtree before we consider it
                        a possible match across code units. (default: 1)
  -t, --types {all,loose,Identifier,PrivateName,Literals,Programs,Functions,Stat
ements,Declarations,Misc,Expressions,Template Literals,Patterns,Classes,Modules}
 [{all,loose,Identifier,PrivateName,Literals,Programs,Functions,Statements,Decla
rations,Misc,Expressions,Template Literals,Patterns,Classes,Modules} ...]
                        Which AST nodes to include in the code graph when
                        comparing code units. You can also use the special
                        cases 'all' to include all AST nodes, or 'loose', to
                        include just the following node types: Programs,
                        Functions, Declarations, Statements (default: ['all'])
  -w, --workspace WORKSPACE
                        Path to a directory that exists and be written to, or
                        does not exist and can be created. This directory will
                        be used to create a child program to convert
                        JavaScript code to GraphML. (default:
                        workspace/js2graphml)
