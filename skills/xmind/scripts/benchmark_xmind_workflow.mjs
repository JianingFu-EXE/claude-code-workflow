#!/usr/bin/env node

import { mkdtemp, readFile, rm } from 'fs/promises';
import { dirname, join, resolve } from 'path';
import { fileURLToPath } from 'url';
import { tmpdir } from 'os';
import {
    readSourceDocument,
    readXmindContentJson,
    renderSourceToXmind,
} from './xmind_lib.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = resolve(__dirname, '..');
const fixturesDir = resolve(rootDir, 'fixtures');

async function renderedContentBytes(sourceFileName) {
    const tempDir = await mkdtemp(join(tmpdir(), 'xmind-bench-'));
    try {
        const sourcePath = resolve(fixturesDir, sourceFileName);
        const sourceDocument = await readSourceDocument(sourcePath);
        const outputPath = resolve(tempDir, sourceFileName.replace('.source.json', '.xmind'));
        await renderSourceToXmind(sourceDocument, outputPath);
        const content = await readXmindContentJson(outputPath);
        return Buffer.byteLength(JSON.stringify(content));
    } finally {
        await rm(tempDir, { recursive: true, force: true });
    }
}

async function main() {
    const currentSkillBytes = Buffer.byteLength(await readFile(resolve(rootDir, 'SKILL.md'), 'utf8'));
    const legacySkillBytes = Buffer.byteLength(await readFile(resolve(fixturesDir, 'legacy_skill_prompt_snapshot.md'), 'utf8'));
    const currentRevisionBytes = Buffer.byteLength(await readFile(resolve(fixturesDir, 'default_revision_request.txt'), 'utf8'));
    const legacyRevisionInstructionBytes = Buffer.byteLength(await readFile(resolve(fixturesDir, 'legacy_revision_request.txt'), 'utf8'));
    const richSourceBytes = Buffer.byteLength(await readFile(resolve(fixturesDir, 'rich_outline_v01.source.json'), 'utf8'));

    const currentRenderedBytes = await renderedContentBytes('lean_outline_v01.source.json');
    const legacyRenderedBytes = await renderedContentBytes('rich_outline_v01.source.json');

    const currentScore = currentSkillBytes + currentRevisionBytes + currentRenderedBytes;
    const legacyRevisionBytes = legacyRevisionInstructionBytes + richSourceBytes + legacyRenderedBytes;
    const legacyScore = legacySkillBytes + legacyRevisionBytes + legacyRenderedBytes;
    const reductionRatio = legacyScore === 0 ? 0 : 1 - (currentScore / legacyScore);

    console.log(`xmind_cost_score=${currentScore}`);
    console.log(`baseline_cost_score=${legacyScore}`);
    console.log(`reduction_ratio=${reductionRatio.toFixed(4)}`);
    console.log(`reduction_percent=${(reductionRatio * 100).toFixed(2)}`);
}

main().catch((error) => {
    console.error(`Error: ${error.message}`);
    process.exit(1);
});
