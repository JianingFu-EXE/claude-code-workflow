#!/usr/bin/env node

import { resolve } from 'path';
import {
    deriveNextSourcePath,
    readSourceDocument,
    writeSourceDocument,
} from './xmind_lib.mjs';

function getArg(flag) {
    const index = process.argv.indexOf(flag);
    return index >= 0 ? process.argv[index + 1] : undefined;
}

async function main() {
    const sourcePath = getArg('--source') ?? process.argv[2];
    if (!sourcePath) throw new Error('Usage: node prepare_revision.mjs --source <map_vNN.source.json> [--out path]');

    const resolvedSourcePath = resolve(sourcePath);
    const nextSourcePath = getArg('--out')
        ? resolve(getArg('--out'))
        : deriveNextSourcePath(resolvedSourcePath);

    const sourceDocument = await readSourceDocument(resolvedSourcePath);
    const nextVersionMatch = nextSourcePath.match(/_v(\d+)\.source\.json$/);
    const nextVersion = nextVersionMatch ? Number(nextVersionMatch[1]) : (sourceDocument.document.version ?? 1) + 1;

    const clonedDocument = {
        ...sourceDocument,
        document: {
            ...sourceDocument.document,
            version: nextVersion,
            basedOn: resolvedSourcePath,
            updatedAt: new Date().toISOString(),
        },
    };

    await writeSourceDocument(clonedDocument, nextSourcePath);
    console.log(`Prepared revision source: ${nextSourcePath}`);
}

main().catch((error) => {
    console.error(`Error: ${error.message}`);
    process.exit(1);
});
