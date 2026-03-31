#!/usr/bin/env node

import { mkdtemp, readFile, rm, writeFile } from 'fs/promises';
import { dirname, join, resolve } from 'path';
import { fileURLToPath } from 'url';
import { tmpdir } from 'os';
import {
    collectTitles,
    countTopics,
    deriveNextSourcePath,
    listZipEntries,
    readJson,
    readSourceDocument,
    readXmindContentJson,
    renderSourceToXmind,
    writeLatestPointer,
    writeSourceDocument,
} from './xmind_lib.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = resolve(__dirname, '..');
const fixturesDir = resolve(rootDir, 'fixtures');

function assert(condition, message) {
    if (!condition) throw new Error(message);
}

function getFirstSheet(sourceDocument) {
    return sourceDocument.sheets[0];
}

function findTopicById(topic, id) {
    if (topic.id === id) return topic;
    for (const child of topic.children ?? []) {
        const found = findTopicById(child, id);
        if (found) return found;
    }
    return null;
}

function flattenTopicTitles(topic, prefix = '', output = []) {
    const path = prefix ? `${prefix}/${topic.title}` : topic.title;
    output.push(path);
    const children = Array.isArray(topic.children)
        ? topic.children
        : [
            ...(topic.children?.attached ?? []),
            ...(topic.children?.detached ?? []),
        ];
    for (const child of children) flattenTopicTitles(child, path, output);
    return output;
}

async function renderFixture(tempDir, fileName) {
    const sourcePath = resolve(fixturesDir, fileName);
    const sourceDocument = await readSourceDocument(sourcePath);
    const outputPath = resolve(tempDir, fileName.replace('.source.json', '.xmind'));
    await renderSourceToXmind(sourceDocument, outputPath);
    const content = await readXmindContentJson(outputPath);
    const zipListing = await listZipEntries(outputPath);
    return { sourcePath, sourceDocument, outputPath, content, zipListing };
}

async function main() {
    const tempDir = await mkdtemp(join(tmpdir(), 'xmind-validate-'));

    try {
        const lean = await renderFixture(tempDir, 'lean_outline_v01.source.json');
        const balanced = await renderFixture(tempDir, 'balanced_outline_v01.source.json');
        const rich = await renderFixture(tempDir, 'rich_outline_v01.source.json');

        for (const rendered of [lean, balanced, rich]) {
            assert(rendered.zipListing.includes('content.json'), `${rendered.outputPath} is missing content.json`);
            assert(rendered.zipListing.includes('metadata.json'), `${rendered.outputPath} is missing metadata.json`);
            assert(rendered.zipListing.includes('manifest.json'), `${rendered.outputPath} is missing manifest.json`);

            const sheet = rendered.content[0];
            assert(sheet.title === 'Launch Plan', 'Sheet title was not preserved');
            assert(sheet.revisionId, 'Sheet revisionId was not added');
            assert(countTopics(getFirstSheet(rendered.sourceDocument).rootTopic) === countTopics(sheet.rootTopic), 'Topic count changed during render');
            const renderedTitles = collectTitles(sheet.rootTopic);
            assert(renderedTitles.includes('Project Launch'), 'Rendered root topic title missing');
            assert(renderedTitles.includes('Analytics gaps'), 'Rendered child topic title missing');
            assert(sheet.rootTopic.labels?.length === 1, 'Root labels were not preserved');
        }

        const leanContentBytes = Buffer.byteLength(JSON.stringify(lean.content));
        const balancedContentBytes = Buffer.byteLength(JSON.stringify(balanced.content));
        const richContentBytes = Buffer.byteLength(JSON.stringify(rich.content));
        assert(leanContentBytes < balancedContentBytes, 'Lean fixture should be smaller than balanced fixture');
        assert(balancedContentBytes < richContentBytes, 'Balanced fixture should be smaller than rich fixture');

        const extractedInput = await readXmindContentJson(rich.outputPath);
        assert(extractedInput[0].rootTopic.title === 'Project Launch', 'Rendered rich fixture could not be re-read');

        const importedSource = await readSourceDocument(lean.sourcePath);
        const nextSourcePath = deriveNextSourcePath(lean.sourcePath);
        const clonedSource = structuredClone(importedSource);
        clonedSource.document = {
            ...clonedSource.document,
            version: 2,
            basedOn: lean.sourcePath,
            updatedAt: new Date().toISOString(),
        };
        const revisedBranch = findTopicById(clonedSource.sheets[0].rootTopic, 'risk-2');
        assert(revisedBranch, 'Could not find target branch for revision test');
        revisedBranch.title = 'Analytics instrumentation gaps';
        revisedBranch.notes = { plain: 'Only this branch should change between v01 and v02.' };
        await writeSourceDocument(clonedSource, nextSourcePath);

        const revisedOutputPath = resolve(tempDir, 'lean_outline_v02.xmind');
        await renderSourceToXmind(clonedSource, revisedOutputPath);
        await writeLatestPointer({
            inputPath: nextSourcePath,
            stem: clonedSource.document.stem,
            version: clonedSource.document.version,
            sourcePath: nextSourcePath,
            xmindPath: revisedOutputPath,
        });

        const originalPaths = flattenTopicTitles(importedSource.sheets[0].rootTopic);
        const revisedContent = await readXmindContentJson(revisedOutputPath);
        const revisedPaths = flattenTopicTitles(revisedContent[0].rootTopic);
        const pathDiff = revisedPaths.filter((value, index) => value !== originalPaths[index]);
        assert(pathDiff.length === 1, 'Revision test should change only one topic path');
        assert(pathDiff[0].includes('Analytics instrumentation gaps'), 'Revision did not update the target branch');

        const latestPointerPath = resolve(dirname(nextSourcePath), `${clonedSource.document.stem}.latest.json`);
        const latestPointer = await readJson(latestPointerPath);
        assert(latestPointer.latestVersion === 2, '.latest.json did not advance to v02');
        assert(latestPointer.latestSourcePath === nextSourcePath, '.latest.json has the wrong source path');
        assert(latestPointer.latestXmindPath === revisedOutputPath, '.latest.json has the wrong xmind path');

        const importFixturePath = resolve(tempDir, 'import_roundtrip_v01.source.json');
        await writeFile(importFixturePath, JSON.stringify({
            document: { title: 'Import Roundtrip', stem: 'import_roundtrip', version: 1, detail: 'lean' },
            sheets: [{
                id: 'sheet-import',
                title: 'Import',
                rootTopic: {
                    id: 'root-import',
                    title: 'Import Root',
                    labels: ['import-label'],
                    markers: ['priority-1'],
                    children: [
                        {
                            id: 'child-import',
                            title: 'Internal Link Source',
                            children: [
                                { id: 'child-target', title: 'Internal Link Target' }
                            ]
                        }
                    ]
                },
                relationships: [
                    { sourceId: 'child-import', targetId: 'child-target', title: 'connected' }
                ]
            }]
        }, null, 2));

        const importFixtureDocument = await readSourceDocument(importFixturePath);
        const importFixtureOutput = resolve(tempDir, 'import_roundtrip_v01.xmind');
        await renderSourceToXmind(importFixtureDocument, importFixtureOutput);
        const importedArchive = await readXmindContentJson(importFixtureOutput);
        assert(importedArchive[0].relationships?.length === 1, 'Relationships were not rendered for import roundtrip fixture');

        console.log('Fixture validation passed');
        console.log(`lean_content_bytes=${leanContentBytes}`);
        console.log(`balanced_content_bytes=${balancedContentBytes}`);
        console.log(`rich_content_bytes=${richContentBytes}`);
    } finally {
        await rm(tempDir, { recursive: true, force: true });
    }
}

main().catch((error) => {
    console.error(`Error: ${error.message}`);
    process.exit(1);
});
