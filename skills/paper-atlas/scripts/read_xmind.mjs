#!/usr/bin/env node

// XMind file reader - extracts hierarchy as JSON from .xmind files
// Usage: node read_xmind.mjs <path-to-xmind-file>
// Output: JSON hierarchy to stdout

import { readFileSync } from 'fs';
import { inflateRawSync } from 'zlib';
import { resolve } from 'path';

// ─── Minimal ZIP reader ───

function readZip(buf) {
    // Find End of Central Directory
    let eocdOffset = -1;
    for (let i = buf.length - 22; i >= 0; i--) {
        if (buf.readUInt32LE(i) === 0x06054b50) { eocdOffset = i; break; }
    }
    if (eocdOffset < 0) throw new Error('Not a valid ZIP file');

    const cdOffset = buf.readUInt32LE(eocdOffset + 16);
    const entryCount = buf.readUInt16LE(eocdOffset + 10);
    const files = {};
    let pos = cdOffset;

    for (let i = 0; i < entryCount; i++) {
        if (buf.readUInt32LE(pos) !== 0x02014b50) throw new Error('Invalid central directory');
        const compression = buf.readUInt16LE(pos + 10);
        const compSize = buf.readUInt32LE(pos + 20);
        const uncompSize = buf.readUInt32LE(pos + 24);
        const nameLen = buf.readUInt16LE(pos + 28);
        const extraLen = buf.readUInt16LE(pos + 30);
        const commentLen = buf.readUInt16LE(pos + 32);
        const localOffset = buf.readUInt32LE(pos + 42);
        const name = buf.toString('utf-8', pos + 46, pos + 46 + nameLen);

        // Read from local header
        const localNameLen = buf.readUInt16LE(localOffset + 26);
        const localExtraLen = buf.readUInt16LE(localOffset + 28);
        const dataStart = localOffset + 30 + localNameLen + localExtraLen;
        const rawData = buf.subarray(dataStart, dataStart + compSize);

        if (compression === 8) {
            files[name] = inflateRawSync(rawData);
        } else if (compression === 0) {
            files[name] = rawData;
        }

        pos += 46 + nameLen + extraLen + commentLen;
    }
    return files;
}

// ─── Hierarchy extractor ───

function extractHierarchy(topic, depth = 0) {
    const node = { title: topic.title || '(untitled)' };
    if (topic.href) node.href = topic.href;
    if (topic.notes) {
        if (topic.notes.plain?.content) node.notes = topic.notes.plain.content;
        else if (topic.notes.realHTML?.content) node.notesHtml = topic.notes.realHTML.content;
    }
    if (topic.labels?.length) node.labels = topic.labels;

    const children = [];
    if (topic.children?.attached) {
        for (const child of topic.children.attached) {
            children.push(extractHierarchy(child, depth + 1));
        }
    }
    if (children.length > 0) node.children = children;
    return node;
}

function extractOutlineText(node, indent = 0) {
    const prefix = '#'.repeat(indent + 1);
    let text = indent < 6 ? `${prefix} ${node.title}\n` : `${'  '.repeat(indent - 6)}- ${node.title}\n`;
    if (node.href) text += `${'  '.repeat(indent)}  Link: ${node.href}\n`;
    if (node.notes) text += `${'  '.repeat(indent)}  Notes: ${node.notes}\n`;
    if (node.children) {
        for (const child of node.children) {
            text += extractOutlineText(child, indent + 1);
        }
    }
    return text;
}

// ─── Main ───

const filePath = process.argv[2];
if (!filePath) {
    console.error('Usage: node read_xmind.mjs <path-to-xmind-file>');
    process.exit(1);
}

const buf = readFileSync(resolve(filePath));
const files = readZip(buf);
const contentRaw = files['content.json'];
if (!contentRaw) {
    console.error('No content.json found in .xmind file');
    process.exit(1);
}

const sheets = JSON.parse(contentRaw.toString('utf-8'));
const output = {
    sheets: sheets.map(sheet => ({
        title: sheet.title,
        rootTopic: extractHierarchy(sheet.rootTopic),
    })),
};

// Output both JSON and readable outline
const outline = output.sheets.map(s => extractOutlineText(s.rootTopic)).join('\n');
console.log(JSON.stringify({ ...output, outline }, null, 2));
