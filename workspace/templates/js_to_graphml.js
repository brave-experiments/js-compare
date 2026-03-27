#!/usr/bin/env node

/**
 * This tool is a simple CLI script used to run the babel JS parser on
 * the given JS code (the first argument), and prints to STDOUT a reduced
 * graphml-encoded tree representation of the code's AST.
 */

const { readFileSync } = require("node:fs");

const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;
const { create } = require("xmlbuilder2");

const code = readFileSync(process.argv[2], "utf-8");
const ast = parser.parse(code);

const graphmlNS = {
  xmlns: "http://graphml.graphdrawing.org/xmlns",
  "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
  "xsi:schemaLocation":
    "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd",
};

const root = create({ encoding: "UTF-8", version: "1.0" }).ele(
  "graphml",
  graphmlNS,
);

root.ele("key", {
  id: "label",
  for: "node",
  "attr.name": "label",
  "attr.type": "string",
});
const graph = root.ele("graph", { id: "G", edgedefault: "directed" });

const neverTypes = new Set(["Comment", "Placeholder"]);

// These are based on Babel Parser API
// https://github.com/babel/babel/blob/main/packages/babel-parser/ast/spec.md
const astNodeTypes = {
  Identifier: new Set(["Identifier"]),
  PrivateName: new Set(["PrivateName"]),
  Literals: new Set([
    "RegExpLiteral",
    "NullLiteral",
    "StringLiteral",
    "BooleanLiteral",
    "NumericLiteral",
    "BigIntLiteral",
    "DecimalLiteral",
  ]),
  Programs: new Set(["Program"]),
  Functions: new Set(["Functions"]),
  Statements: new Set([
    "Statement",
    "ExpressionStatement",
    "BlockStatement",
    "EmptyStatement",
    "DebuggerStatement",
    "WithStatement",
    "ReturnStatement",
    "LabeledStatement",
    "BreakStatement",
    "ContinueStatement",
    "IfStatement",
    "SwitchStatement",
    "SwitchCase",
    "ThrowStatement",
    "TryStatement",
    "CatchClause",
    "WhileStatement",
    "DoWhileStatement",
    "ForStatement",
    "ForInStatement",
    "ForOfStatement",
  ]),
  Declarations: new Set([
    "Declaration",
    "FunctionDeclaration",
    "VariableDeclaration",
    "VariableDeclarator",
  ]),
  Misc: new Set([
    "Decorator",
    "Directive",
    "DirectiveLiteral",
    "InterpreterDirective",
  ]),
  Expressions: new Set([
    "Expression",
    "Super",
    "Import",
    "ThisExpression",
    "ArrowFunctionExpression",
    "YieldExpression",
    "AwaitExpression",
    "ArrayExpression",
    "ObjectExpression",
    "ObjectMember",
    "ObjectProperty",
    "ObjectMethod",
    "FunctionExpression",
    "UnaryExpression",
    "UpdateExpression",
    "BinaryExpression",
    "AssignmentExpression",
    "LogicalExpression",
    "SpreadElement",
    "ArgumentPlaceholder",
    "MemberExpression",
    "OptionalMemberExpression",
    "BindExpression",
    "ConditionalExpression",
    "CallExpression",
    "OptionalCallExpression",
    "NewExpression",
    "SequenceExpression",
    "ParenthesizedExpression",
    "DoExpression",
    "ModuleExpression",
    "TopicReference",
  ]),
  "Template Literals": new Set([
    "TemplateLiteral",
    "TaggedTemplateExpression",
    "TemplateElement",
  ]),
  Patterns: new Set([
    "Pattern",
    "AssignmentProperty",
    "ObjectPattern",
    "ArrayPattern",
    "RestElement",
    "AssignmentPattern",
    "VoidPattern",
  ]),
  Classes: new Set([
    "Class",
    "ClassBody",
    "ClassMethod",
    "ClassPrivateMethod",
    "ClassProperty",
    "ClassPrivateProperty",
    "ClassAccessorProperty",
    "StaticBlock",
    "ClassDeclaration",
    "ClassExpression",
    "MetaProperty",
  ]),
  Modules: new Set([
    "ModuleSpecifier",
    "ImportDeclaration",
    "ImportSpecifier",
    "ImportDefaultSpecifier",
    "ImportNamespaceSpecifier",
    "ImportAttribute",
    "ExportDeclaration",
    "ExportNamedDeclaration",
    "ExportSpecifier",
    "ExportNamespaceSpecifier",
    "ExportDefaultSpecifier",
    "OptFunctionDeclaration",
    "OptClassDeclaration",
    "ExportDefaultDeclaration",
    "ExportAllDeclaration",
  ]),
};

const nodeCategoriesToInclude =
  process.argv.length > 3
    ? process.argv.slice(3)
    : Object.keys(astNodeTypes);

let nodeTypesToInclude = new Set();
for (const aCategory of nodeCategoriesToInclude) {
  const nodeTypesInCategory = astNodeTypes[aCategory];
  if (nodeTypesInCategory === undefined) {
    throw new Error(`Unrecognized AST category type: "${aCategory}"`);
  }
  nodeTypesToInclude = nodeTypesToInclude.union(nodeTypesInCategory);
}

traverse(ast, {
  enter(path) {
    const nodeType = path.node.type;
    // Do not include comment nodes, or other nodes that do not have
    // structural significance in the program.
    if (neverTypes.has(nodeType)) {
      return;
    }

    if (nodeTypesToInclude.has(nodeType) === false) {
      return;
    }

    const nodeId = `${nodeType}_${path.node.start}`;

    const node = graph.ele("node", { id: nodeId });
    node.ele("data", { key: "label" }).txt(nodeType);

    if (!path.parentPath) {
      return;
    }

    let parentPath = path.parentPath;
    while (nodeTypesToInclude.has(parentPath.node.type) === false) {
      parentPath = parentPath.parentPath;
      if (!parentPath) {
        throw new Error("Could not find valid parent node when walking AST.");
      }
    }

    const parentType = parentPath.node.type;
    const parentStart = parentPath.node.start;
    const parentId = `${parentType}_${parentStart}`;
    graph.ele("edge", {
      id: `e_${parentId}_${nodeId}`,
      source: parentId,
      target: nodeId,
    });
  },
});

console.log(root.end({ prettyPrint: true }));
