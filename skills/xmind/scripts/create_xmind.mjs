#!/usr/bin/env node

import { resolve } from 'path';
import {
    deriveXmindPathFromSource,
    normalizeSourceDocument,
    readJson,
    readSourceDocument,
    renderSourceToXmind,
    writeLatestPointer,
} from './xmind_lib.mjs';

function getArg(flag) {
    const index = process.argv.indexOf(flag);
    return index >= 0 ? process.argv[index + 1] : undefined;
}

async function readStdin() {
    let raw = '';
    for await (const chunk of process.stdin) raw += chunk;
    return raw.trim();
}

async function main() {
    const sourcePath = getArg('--source');
    let explicitOutputPath = getArg('--path');
    const stdinRaw = sourcePath ? '' : await readStdin();

    let sourceDocument;
    let effectiveSourcePath = sourcePath ? resolve(sourcePath) : undefined;

    if (sourcePath) {
        sourceDocument = await readSourceDocument(sourcePath);
    } else if (stdinRaw) {
        const input = JSON.parse(stdinRaw);
        sourceDocument = normalizeSourceDocument(input, input.path ?? undefined);
        if (input.path?.endsWith('.source.json')) effectiveSourcePath = resolve(input.path);
        // Backward compat: if input.path ends with .xmind, use it as explicit output
        if (!explicitOutputPath && input.path?.toLowerCase().endsWith('.xmind')) {
            explicitOutputPath = resolve(input.path);
        }
    } else {
        throw new Error('Provide --source <path> or JSON via stdin.');
    }

    const outputPath = explicitOutputPath
        ? resolve(explicitOutputPath)
        : effectiveSourcePath
            ? deriveXmindPathFromSource(effectiveSourcePath)
            : resolve(process.cwd(), `${sourceDocument.document.stem ?? 'mindmap'}_v${String(sourceDocument.document.version ?? 1).padStart(2, '0')}.xmind`);

    if (!outputPath.toLowerCase().endsWith('.xmind')) {
        throw new Error('Output path must end with .xmind');
    }

    const renderedPath = await renderSourceToXmind(sourceDocument, outputPath);

    if (effectiveSourcePath) {
        await writeLatestPointer({
            inputPath: effectiveSourcePath,
            stem: sourceDocument.document.stem,
            version: sourceDocument.document.version,
            sourcePath: effectiveSourcePath,
            xmindPath: renderedPath,
        });
    }

    console.log(`Rendered: ${renderedPath}`);
}

main().catch((error) => {
    console.error(`Error: ${error.message}`);
    process.exit(1);
});
