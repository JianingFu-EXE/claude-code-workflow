#!/usr/bin/env node

import { resolve } from 'path';
import {
    deriveVersionedSourcePath,
    extractToSourceDocument,
    writeLatestPointer,
    writeSourceDocument,
} from './xmind_lib.mjs';

function getArg(flag) {
    const index = process.argv.indexOf(flag);
    return index >= 0 ? process.argv[index + 1] : undefined;
}

async function main() {
    const xmindPath = getArg('--input') ?? process.argv[2];
    if (!xmindPath) throw new Error('Usage: node extract_xmind.mjs <map.xmind> [--out path]');

    const resolvedXmindPath = resolve(xmindPath);
    const outputPath = getArg('--out')
        ? resolve(getArg('--out'))
        : deriveVersionedSourcePath(resolvedXmindPath);

    const sourceDocument = await extractToSourceDocument(resolvedXmindPath);
    await writeSourceDocument(sourceDocument, outputPath);
    const pointerPath = await writeLatestPointer({
        inputPath: outputPath,
        stem: sourceDocument.document.stem,
        version: sourceDocument.document.version,
        sourcePath: outputPath,
        xmindPath: resolvedXmindPath,
    });

    console.log(`Extracted source: ${outputPath}`);
    console.log(`Updated pointer: ${pointerPath}`);
}

main().catch((error) => {
    console.error(`Error: ${error.message}`);
    process.exit(1);
});
