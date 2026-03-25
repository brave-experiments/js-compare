#!/usr/bin/env node

/**
 * This tool is a simple CLI script used to run the babel JS parser on
 * the given JS code (the first argument), and prints to STDOUT a reduced
 * graphml-encoded tree representation of the code's AST.
 */

const { readFileSync } = require('node:fs');

const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const { create } = require('xmlbuilder2');

const code = readFileSync(process.argv[2], "utf-8");
const ast = parser.parse(code);

const graphmlNS = {
  "xmlns": "http://graphml.graphdrawing.org/xmlns",
  "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
  "xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd",
};

const root = create({ version: '1.0', encoding: 'UTF-8' })
  .ele('graphml', graphmlNS);

root.ele('key', {
  id: 'label',
  for: 'node',
  'attr.name':
  'label',
  'attr.type': 'string'
});
const graph = root.ele('graph', { id: 'G', edgedefault: 'directed' });

traverse(ast, {
  enter(path) {
    const nodeType = path.node.type;
    // Do not include comment nodes, or other nodes that do not have
    // structural significance in the program.
    if (nodeType.includes('Comment') || nodeType === 'Placeholder') {
      return; 
    }

    const nodeId = `${nodeType}_${path.node.start}`;
    
    const node = graph.ele('node', { id: nodeId });
    node.ele('data', { key: 'label' }).txt(nodeType);

    if (!path.parentPath) {
      return;
    }

    const parentType = path.parentPath.node.type;
    const parentStart = path.parentPath.node.start;
    const parentId = `${parentType}_${parentStart}`;
    graph.ele('edge', { 
      id: `e_${parentId}_${nodeId}`, 
      source: parentId, 
      target: nodeId 
    });
  }
});

console.log(root.end({ prettyPrint: true }));
