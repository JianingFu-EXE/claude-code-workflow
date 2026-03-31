import { execFile } from 'child_process';
import { promisify } from 'util';
import { mkdir, mkdtemp, readFile, rename, rm, writeFile } from 'fs/promises';
import { dirname, extname, basename, join, resolve } from 'path';
import { randomUUID, createHash } from 'crypto';
import { deflateRawSync } from 'zlib';
import { tmpdir } from 'os';

const execFileAsync = promisify(execFile);

export function generateId() {
    return randomUUID().replace(/-/g, '').substring(0, 26);
}

function dateToDos(date = new Date()) {
    const year = Math.max(1980, date.getFullYear());
    const dosTime = ((date.getHours() & 0x1f) << 11)
        | ((date.getMinutes() & 0x3f) << 5)
        | Math.floor(date.getSeconds() / 2);
    const dosDate = (((year - 1980) & 0x7f) << 9)
        | (((date.getMonth() + 1) & 0x0f) << 5)
        | (date.getDate() & 0x1f);
    return { dosTime, dosDate };
}

function crc32(buf) {
    let crc = 0xFFFFFFFF;
    for (let i = 0; i < buf.length; i++) {
        crc ^= buf[i];
        for (let j = 0; j < 8; j++) {
            crc = (crc >>> 1) ^ (crc & 1 ? 0xEDB88320 : 0);
        }
    }
    return (crc ^ 0xFFFFFFFF) >>> 0;
}

export function buildZip(files) {
    const entries = [];
    const centralHeaders = [];
    let offset = 0;

    for (const file of files) {
        const nameBytes = Buffer.from(file.name, 'utf-8');
        const data = Buffer.isBuffer(file.data) ? file.data : Buffer.from(file.data);
        const compressed = deflateRawSync(data);
        const crc = crc32(data);
        const modifiedAt = file.modifiedAt ?? new Date();
        const { dosTime, dosDate } = dateToDos(modifiedAt);

        const localHeader = Buffer.alloc(30);
        localHeader.writeUInt32LE(0x04034b50, 0);
        localHeader.writeUInt16LE(20, 4);
        localHeader.writeUInt16LE(0, 6);
        localHeader.writeUInt16LE(8, 8);
        localHeader.writeUInt16LE(dosTime, 10);
        localHeader.writeUInt16LE(dosDate, 12);
        localHeader.writeUInt32LE(crc, 14);
        localHeader.writeUInt32LE(compressed.length, 18);
        localHeader.writeUInt32LE(data.length, 22);
        localHeader.writeUInt16LE(nameBytes.length, 26);
        localHeader.writeUInt16LE(0, 28);

        const entry = Buffer.concat([localHeader, nameBytes, compressed]);
        entries.push(entry);

        const cdHeader = Buffer.alloc(46);
        cdHeader.writeUInt32LE(0x02014b50, 0);
        cdHeader.writeUInt16LE(20, 4);
        cdHeader.writeUInt16LE(20, 6);
        cdHeader.writeUInt16LE(0, 8);
        cdHeader.writeUInt16LE(8, 10);
        cdHeader.writeUInt16LE(dosTime, 12);
        cdHeader.writeUInt16LE(dosDate, 14);
        cdHeader.writeUInt32LE(crc, 16);
        cdHeader.writeUInt32LE(compressed.length, 20);
        cdHeader.writeUInt32LE(data.length, 24);
        cdHeader.writeUInt16LE(nameBytes.length, 28);
        cdHeader.writeUInt16LE(0, 30);
        cdHeader.writeUInt16LE(0, 32);
        cdHeader.writeUInt16LE(0, 34);
        cdHeader.writeUInt16LE(0, 36);
        cdHeader.writeUInt32LE(0, 38);
        cdHeader.writeUInt32LE(offset, 42);

        centralHeaders.push(Buffer.concat([cdHeader, nameBytes]));
        offset += entry.length;
    }

    const centralDir = Buffer.concat(centralHeaders);
    const eocd = Buffer.alloc(22);
    eocd.writeUInt32LE(0x06054b50, 0);
    eocd.writeUInt16LE(0, 4);
    eocd.writeUInt16LE(0, 6);
    eocd.writeUInt16LE(files.length, 8);
    eocd.writeUInt16LE(files.length, 10);
    eocd.writeUInt32LE(centralDir.length, 12);
    eocd.writeUInt32LE(offset, 16);
    eocd.writeUInt16LE(0, 20);

    return Buffer.concat([...entries, centralDir, eocd]);
}

function parseVersionInfo(inputPath, preferredStem) {
    const resolvedPath = resolve(inputPath);
    const dir = dirname(resolvedPath);
    const fileName = basename(resolvedPath);
    const sourceSuffix = '.source.json';
    const bareName = fileName.endsWith(sourceSuffix)
        ? fileName.slice(0, -sourceSuffix.length)
        : fileName.slice(0, fileName.length - extname(fileName).length);
    const match = bareName.match(/^(.*)_v(\d+)$/);
    const baseStem = preferredStem ?? (match ? match[1] : bareName);
    const version = match ? Number(match[2]) : null;
    const digits = match ? Math.max(2, match[2].length) : 2;
    return {
        resolvedPath,
        dir,
        fileName,
        bareName,
        baseStem,
        version,
        digits,
    };
}

function formatVersion(version, digits = 2) {
    return `v${String(version).padStart(digits, '0')}`;
}

export function deriveVersionedSourcePath(inputPath, defaultVersion = 1, preferredStem) {
    const info = parseVersionInfo(inputPath, preferredStem);
    const version = info.version ?? defaultVersion;
    return join(info.dir, `${info.baseStem}_${formatVersion(version, info.digits)}.source.json`);
}

export function deriveNextSourcePath(sourcePath) {
    const info = parseVersionInfo(sourcePath);
    const version = (info.version ?? 1) + 1;
    return join(info.dir, `${info.baseStem}_${formatVersion(version, info.digits)}.source.json`);
}

export function deriveXmindPathFromSource(sourcePath) {
    const info = parseVersionInfo(sourcePath);
    const version = info.version ?? 1;
    return join(info.dir, `${info.baseStem}_${formatVersion(version, info.digits)}.xmind`);
}

export function deriveLatestPointerPath(inputPath, preferredStem) {
    const info = parseVersionInfo(inputPath, preferredStem);
    return join(info.dir, `${info.baseStem}.latest.json`);
}

export function getVersionNumber(inputPath) {
    return parseVersionInfo(inputPath).version;
}

export async function readJson(filePath) {
    return JSON.parse(await readFile(resolve(filePath), 'utf8'));
}

export function normalizeNotes(notes) {
    if (!notes) return undefined;
    if (typeof notes === 'string') return { plain: notes };
    const plain = notes.plain?.content ?? notes.plain;
    const html = notes.realHTML?.content ?? notes.html;
    if (!plain && !html) return undefined;
    return {
        ...(plain ? { plain } : {}),
        ...(html ? { html } : {}),
    };
}

function normalizeRelationships(relationships) {
    if (!relationships?.length) return undefined;
    return relationships.map((relationship) => ({
        ...(relationship.sourceId ? { sourceId: relationship.sourceId } : {}),
        ...(relationship.sourceTitle ? { sourceTitle: relationship.sourceTitle } : {}),
        ...(relationship.targetId ? { targetId: relationship.targetId } : {}),
        ...(relationship.targetTitle ? { targetTitle: relationship.targetTitle } : {}),
        ...(relationship.title ? { title: relationship.title } : {}),
        ...(relationship.shape ? { shape: relationship.shape } : {}),
        ...(relationship.controlPoints ? { controlPoints: relationship.controlPoints } : {}),
    }));
}

function normalizeDependencies(dependencies) {
    if (!dependencies?.length) return undefined;
    return dependencies.map((dependency) => ({
        ...(dependency.id ? { targetId: dependency.id } : {}),
        ...(dependency.targetId ? { targetId: dependency.targetId } : {}),
        ...(dependency.targetTitle ? { targetTitle: dependency.targetTitle } : {}),
        type: dependency.type,
        ...(dependency.lag !== undefined ? { lag: dependency.lag } : {}),
    }));
}

function normalizeTopic(topic) {
    const notes = normalizeNotes(topic.notes);
    const taskExtension = topic.extensions?.find((extension) => extension.provider === 'org.xmind.ui.task');
    const plannedTask = taskExtension?.content;
    const result = {
        id: topic.id ?? generateId(),
        title: topic.title ?? '',
    };

    if (notes) result.notes = notes;
    if (topic.labels?.length) result.labels = topic.labels;
    if (topic.markers?.length) result.markers = topic.markers.map((marker) => marker.markerId ?? marker);
    if (topic.href) {
        if (topic.href.startsWith('xmind:#')) {
            result.linkToTopicId = topic.href.slice('xmind:#'.length);
        } else {
            result.href = topic.href;
        }
    }
    if (topic.structureClass) result.structureClass = topic.structureClass;
    if (topic.position) result.position = topic.position;
    if (topic.image) result.image = topic.image;
    if (topic.style?.properties) {
        const props = { ...topic.style.properties };
        const shapeClass = props['shape-class'];
        if (shapeClass) result.shape = shapeClass;
        // Preserve all non-shape style properties (font, color, fill, etc.)
        delete props['shape-class'];
        if (Object.keys(props).length > 0) result.styleProperties = props;
    }
    if (plannedTask) {
        if (plannedTask.status) result.taskStatus = plannedTask.status;
        if (plannedTask.progress !== undefined) result.progress = plannedTask.progress;
        if (plannedTask.priority !== undefined) result.priority = plannedTask.priority;
        if (plannedTask.start !== undefined) result.startDate = new Date(plannedTask.start).toISOString();
        if (plannedTask.due !== undefined) result.dueDate = new Date(plannedTask.due).toISOString();
        if (!result.startDate && plannedTask.duration !== undefined) {
            result.durationDays = plannedTask.duration / 86400000;
        }
        const dependencies = normalizeDependencies(plannedTask.dependencies);
        if (dependencies) result.dependencies = dependencies;
    }
    if (topic.boundaries?.length) result.boundaries = topic.boundaries;
    if (topic.summaries?.length && topic.summary?.length) {
        result.summaryTopics = topic.summaries.map((summary, index) => ({
            range: summary.range,
            title: topic.summary[index]?.title ?? '',
        }));
    }
    if (topic.children?.callout?.length) {
        result.callouts = topic.children.callout.map((callout) => callout.title);
    }

    const attachedChildren = topic.children?.attached?.map(normalizeTopic) ?? [];
    if (attachedChildren.length) result.children = attachedChildren;
    return result;
}

export function normalizeSourceDocument(input, fallbackPath) {
    if (input.document && Array.isArray(input.sheets)) {
        return {
            document: {
                title: input.document.title ?? 'Untitled Map',
                detail: input.document.detail ?? 'lean',
                ...(input.document.stem ? { stem: input.document.stem } : {}),
                ...(input.document.version !== undefined ? { version: input.document.version } : {}),
                ...(input.document.updatedAt ? { updatedAt: input.document.updatedAt } : {}),
                ...(input.document.basedOn ? { basedOn: input.document.basedOn } : {}),
                ...(input.document.importedFrom ? { importedFrom: input.document.importedFrom } : {}),
            },
            sheets: input.sheets,
        };
    }

    const stemInfo = fallbackPath ? parseVersionInfo(fallbackPath) : null;
    const title = stemInfo?.baseStem ?? 'Untitled Map';
    const version = stemInfo?.version ?? 1;
    const sheets = input.sheets ?? [];
    return {
        document: {
            title,
            stem: stemInfo?.baseStem ?? title,
            version,
            detail: 'lean',
        },
        sheets,
    };
}

export async function readSourceDocument(sourcePath) {
    const raw = await readJson(sourcePath);
    return normalizeSourceDocument(raw, sourcePath);
}

export async function readXmindContentJson(xmindPath) {
    const { stdout } = await execFileAsync('unzip', ['-p', resolve(xmindPath), 'content.json'], {
        maxBuffer: 32 * 1024 * 1024,
    });
    return JSON.parse(stdout);
}

export async function extractToSourceDocument(xmindPath) {
    const sheets = await readXmindContentJson(xmindPath);
    return {
        document: {
            title: basename(xmindPath, extname(xmindPath)),
            stem: parseVersionInfo(xmindPath).baseStem,
            version: parseVersionInfo(xmindPath).version ?? 1,
            detail: 'lean',
            importedFrom: resolve(xmindPath),
            updatedAt: new Date().toISOString(),
        },
        sheets: sheets.map((sheet) => ({
            id: sheet.id ?? generateId(),
            title: sheet.title,
            ...(sheet.freePositioning || sheet.topicPositioning === 'free' ? { freePositioning: true } : {}),
            rootTopic: normalizeTopic(sheet.rootTopic),
            ...(sheet.rootTopic?.children?.detached?.length
                ? { detachedTopics: sheet.rootTopic.children.detached.map(normalizeTopic) }
                : {}),
            ...(sheet.relationships?.length
                ? {
                    relationships: sheet.relationships.map((relationship) => ({
                        ...(relationship.end1Id ? { sourceId: relationship.end1Id } : {}),
                        ...(relationship.end2Id ? { targetId: relationship.end2Id } : {}),
                        ...(relationship.title ? { title: relationship.title } : {}),
                        ...(relationship.style?.properties?.['shape-class']
                            ? { shape: relationship.style.properties['shape-class'] }
                            : {}),
                        ...(relationship.controlPoints ? { controlPoints: relationship.controlPoints } : {}),
                    })),
                }
                : {}),
        })),
    };
}

class XMindBuilder {
    constructor() {
        this.titleToId = new Map();
        this.inputIdToBuiltId = new Map();
        this.pendingDependencies = new Map();
        this.pendingLinks = new Map();
        this.attachments = [];
    }

    build(sheets) {
        this.titleToId.clear();
        this.inputIdToBuiltId.clear();
        this.pendingDependencies.clear();
        this.pendingLinks.clear();
        this.attachments = [];

        const builtSheets = [];
        for (const sheet of sheets) {
            const rootTopic = this.buildTopic(sheet.rootTopic);
            const detached = sheet.detachedTopics?.map((topic) => this.buildTopic(topic, { detached: true })) ?? [];
            this.resolveDependencies(rootTopic);
            detached.forEach((topic) => this.resolveDependencies(topic));
            builtSheets.push({ rootTopic, detached, sheet });
        }

        for (const { rootTopic, detached } of builtSheets) {
            this.resolveLinks(rootTopic);
            detached.forEach((topic) => this.resolveLinks(topic));
        }

        return {
            contentJson: builtSheets.map(({ rootTopic, detached, sheet }) => {
                const sheetObject = {
                    id: sheet.id ?? generateId(),
                    revisionId: randomUUID(),
                    class: 'sheet',
                    title: sheet.title,
                    rootTopic,
                    topicOverlapping: 'overlap',
                    theme: {},
                };
                if (sheet.freePositioning) {
                    sheetObject.topicPositioning = 'free';
                    sheetObject.floatingTopicFlexible = true;
                }
                if (detached.length) {
                    if (!sheetObject.rootTopic.children) sheetObject.rootTopic.children = {};
                    sheetObject.rootTopic.children.detached = detached;
                }
                if (this.hasPlannedTasks(sheet.rootTopic)) {
                    sheetObject.extensions = [{
                        provider: 'org.xmind.ui.working-day-settings',
                        content: {
                            id: 'YmFzaWMtY2FsZW5kYXI=',
                            name: 'Basic Calendar',
                            defaultWorkingDays: [1, 2, 3, 4, 5],
                            rules: [],
                        },
                    }];
                }
                if (sheet.relationships?.length) {
                    sheetObject.relationships = sheet.relationships.map((relationship) => {
                        const end1Id = relationship.sourceId
                            ? (this.inputIdToBuiltId.get(relationship.sourceId) ?? relationship.sourceId)
                            : this.titleToId.get(relationship.sourceTitle);
                        const end2Id = relationship.targetId
                            ? (this.inputIdToBuiltId.get(relationship.targetId) ?? relationship.targetId)
                            : this.titleToId.get(relationship.targetTitle);
                        if (!end1Id) throw new Error(`Relationship source not found for sheet "${sheet.title}".`);
                        if (!end2Id) throw new Error(`Relationship target not found for sheet "${sheet.title}".`);
                        const builtRelationship = {
                            id: generateId(),
                            end1Id,
                            end2Id,
                        };
                        if (relationship.title) builtRelationship.title = relationship.title;
                        if (relationship.shape) {
                            builtRelationship.style = {
                                id: generateId(),
                                properties: { 'shape-class': relationship.shape },
                            };
                        }
                        if (relationship.controlPoints) builtRelationship.controlPoints = relationship.controlPoints;
                        return builtRelationship;
                    });
                }
                return sheetObject;
            }),
            attachments: this.attachments,
        };
    }

    async finalize(contentJson, attachments) {
        const fileEntries = { 'content.json': {}, 'metadata.json': {} };
        const resourceFiles = [];

        for (const attachment of attachments) {
            const data = await readFile(resolve(attachment.sourcePath));
            const hash = createHash('sha256').update(data).digest('hex');
            const extension = extname(attachment.sourcePath);
            const resourcePath = `resources/${hash}${extension}`;
            fileEntries[resourcePath] = {};
            resourceFiles.push({ name: resourcePath, data, modifiedAt: new Date() });
            this.setHrefById(contentJson, attachment.topicId, `xap:${resourcePath}`);
        }

        return {
            content: JSON.stringify(contentJson),
            metadata: JSON.stringify({
                dataStructureVersion: '3',
                creator: { name: 'xmind-skill', version: '2.0.0' },
                layoutEngineVersion: '5',
            }),
            manifest: JSON.stringify({ 'file-entries': fileEntries }),
            resourceFiles,
        };
    }

    setHrefById(sheets, topicId, href) {
        for (const sheet of sheets) {
            if (this.setHrefRecursive(sheet.rootTopic, topicId, href)) return;
        }
    }

    setHrefRecursive(topic, topicId, href) {
        if (topic.id === topicId) {
            topic.href = href;
            return true;
        }
        for (const child of topic.children?.attached ?? []) {
            if (this.setHrefRecursive(child, topicId, href)) return true;
        }
        for (const child of topic.children?.callout ?? []) {
            if (this.setHrefRecursive(child, topicId, href)) return true;
        }
        for (const child of topic.children?.detached ?? []) {
            if (this.setHrefRecursive(child, topicId, href)) return true;
        }
        return false;
    }

    resolveLinks(topic) {
        const pendingLink = this.pendingLinks.get(topic.id);
        if (pendingLink) {
            let targetId = pendingLink.targetId
                ? (this.inputIdToBuiltId.get(pendingLink.targetId) ?? pendingLink.targetId)
                : undefined;
            if (!targetId && pendingLink.targetTitle) targetId = this.titleToId.get(pendingLink.targetTitle);
            if (!targetId) throw new Error(`Link target not found for "${topic.title}".`);
            topic.href = `xmind:#${targetId}`;
        }
        for (const child of topic.children?.attached ?? []) this.resolveLinks(child);
        for (const child of topic.children?.callout ?? []) this.resolveLinks(child);
        for (const child of topic.children?.detached ?? []) this.resolveLinks(child);
    }

    resolveDependencies(topic) {
        const dependencies = this.pendingDependencies.get(topic.id);
        if (dependencies?.length && topic.extensions) {
            const taskExtension = topic.extensions.find((extension) => extension.provider === 'org.xmind.ui.task');
            if (taskExtension) {
                taskExtension.content.dependencies = dependencies.map((dependency) => {
                    let targetId = dependency.targetId
                        ? (this.inputIdToBuiltId.get(dependency.targetId) ?? dependency.targetId)
                        : undefined;
                    if (!targetId && dependency.targetTitle) targetId = this.titleToId.get(dependency.targetTitle);
                    if (!targetId) throw new Error(`Dependency target not found for "${topic.title}".`);
                    return {
                        id: targetId,
                        type: dependency.type,
                        lag: dependency.lag ?? 0,
                    };
                });
            }
        }
        for (const child of topic.children?.attached ?? []) this.resolveDependencies(child);
        for (const child of topic.children?.callout ?? []) this.resolveDependencies(child);
    }

    hasPlannedTasks(topic) {
        if (!topic) return false;
        if (topic.startDate || topic.dueDate || topic.progress !== undefined || topic.durationDays !== undefined) {
            return true;
        }
        return (topic.children ?? []).some((child) => this.hasPlannedTasks(child));
    }

    buildTopic(input) {
        const id = input.id ?? generateId();
        this.titleToId.set(input.title, id);
        if (input.id) this.inputIdToBuiltId.set(input.id, id);

        const topic = {
            id,
            class: 'topic',
            title: input.title,
        };

        if (input.structureClass) topic.structureClass = input.structureClass;
        if (input.position) topic.position = input.position;
        if (input.image) topic.image = input.image;
        if (input.shape || input.styleProperties) {
            const properties = {};
            if (input.shape) properties['shape-class'] = input.shape;
            if (input.styleProperties) Object.assign(properties, input.styleProperties);
            topic.style = { id: generateId(), properties };
        }
        if (input.notes) {
            topic.notes = {};
            if (typeof input.notes === 'string') {
                topic.notes.plain = { content: input.notes };
            } else {
                if (input.notes.plain) topic.notes.plain = { content: input.notes.plain };
                if (input.notes.html) topic.notes.realHTML = { content: input.notes.html };
            }
        }
        if (input.attachment) {
            this.attachments.push({ sourcePath: input.attachment, topicId: id });
        } else if (input.href) {
            topic.href = input.href;
        }
        if (input.linkToTopicId || input.linkToTopic) {
            this.pendingLinks.set(id, {
                ...(input.linkToTopicId ? { targetId: input.linkToTopicId } : {}),
                ...(input.linkToTopic ? { targetTitle: input.linkToTopic } : {}),
            });
        }
        if (input.labels?.length) topic.labels = input.labels;
        if (input.markers?.length) topic.markers = input.markers.map((markerId) => ({ markerId }));

        const hasTaskProps = input.taskStatus || input.progress !== undefined
            || input.priority !== undefined || input.startDate || input.dueDate
            || input.durationDays !== undefined || input.dependencies?.length;
        if (hasTaskProps) {
            const content = {};
            if (input.taskStatus) content.status = input.taskStatus;
            if (input.progress !== undefined) content.progress = input.progress;
            if (input.priority !== undefined) content.priority = input.priority;
            if (input.startDate) content.start = new Date(input.startDate).getTime();
            if (input.dueDate) {
                content.due = new Date(input.dueDate).getTime();
                if (input.startDate) {
                    content.duration = new Date(input.dueDate).getTime() - new Date(input.startDate).getTime();
                }
            }
            if (input.durationDays !== undefined && !input.startDate) {
                content.duration = input.durationDays * 86400000;
            }
            if (input.dependencies?.length) this.pendingDependencies.set(id, input.dependencies);
            topic.extensions = [{ provider: 'org.xmind.ui.task', content }];
        }

        if (input.boundaries?.length) topic.boundaries = input.boundaries.map((boundary) => ({
            id: generateId(),
            range: boundary.range,
            ...(boundary.title ? { title: boundary.title } : {}),
        }));
        if (input.summaryTopics?.length) {
            topic.summaries = input.summaryTopics.map((summary) => ({
                id: generateId(),
                range: summary.range,
                topicId: generateId(),
            }));
            topic.summary = input.summaryTopics.map((summary, index) => ({
                id: topic.summaries[index].topicId,
                title: summary.title,
            }));
        }

        const attached = input.children?.length ? input.children.map((child) => this.buildTopic(child)) : undefined;
        const callout = input.callouts?.length ? input.callouts.map((title) => ({ id: generateId(), title })) : undefined;
        if (attached || callout) {
            topic.children = {};
            if (attached) topic.children.attached = attached;
            if (callout) topic.children.callout = callout;
        }

        return topic;
    }
}

function collectImageResources(topic, resources = new Set()) {
    if (topic?.image?.src?.startsWith('xap:resources/')) {
        resources.add(topic.image.src.slice(4)); // strip 'xap:' prefix
    }
    for (const child of topic?.children ?? []) {
        collectImageResources(child, resources);
    }
    return resources;
}

async function extractResourcesFromXmind(xmindPath, resourceNames) {
    const results = [];
    const resolvedPath = resolve(xmindPath);
    for (const name of resourceNames) {
        try {
            const { stdout } = await execFileAsync('unzip', ['-p', resolvedPath, name], {
                maxBuffer: 32 * 1024 * 1024,
                encoding: 'buffer',
            });
            results.push({ name, data: stdout, modifiedAt: new Date() });
        } catch {
            // Resource not found in source archive — skip silently
        }
    }
    return results;
}

export async function renderSourceToXmind(sourceDocument, outputPath) {
    const normalized = normalizeSourceDocument(sourceDocument, outputPath);
    const builder = new XMindBuilder();
    const { contentJson, attachments } = builder.build(normalized.sheets);
    const { content, metadata, manifest, resourceFiles } = await builder.finalize(contentJson, attachments);
    const resolvedOutputPath = resolve(outputPath);
    await mkdir(dirname(resolvedOutputPath), { recursive: true });

    // Collect embedded image resource paths from source sheets
    const imageResources = new Set();
    for (const sheet of normalized.sheets) {
        collectImageResources(sheet.rootTopic, imageResources);
        for (const dt of sheet.detachedTopics ?? []) {
            collectImageResources(dt, imageResources);
        }
    }

    // Extract image resources from the original .xmind if available
    let embeddedResources = [];
    const importedFrom = normalized.document?.importedFrom;
    if (imageResources.size > 0 && importedFrom) {
        embeddedResources = await extractResourcesFromXmind(importedFrom, imageResources);
    }

    // Update manifest with embedded resources
    const manifestObj = JSON.parse(manifest);
    for (const res of embeddedResources) {
        manifestObj['file-entries'][res.name] = {};
    }

    const tempDir = await mkdtemp(join(tmpdir(), 'xmind-render-'));
    const tempPath = join(tempDir, basename(resolvedOutputPath));
    const zipBuffer = buildZip([
        { name: 'content.json', data: Buffer.from(content, 'utf-8'), modifiedAt: new Date() },
        { name: 'metadata.json', data: Buffer.from(metadata, 'utf-8'), modifiedAt: new Date() },
        { name: 'manifest.json', data: Buffer.from(JSON.stringify(manifestObj), 'utf-8'), modifiedAt: new Date() },
        ...resourceFiles,
        ...embeddedResources,
    ]);

    await writeFile(tempPath, zipBuffer);
    await rename(tempPath, resolvedOutputPath);
    await rm(tempDir, { recursive: true, force: true });
    return resolvedOutputPath;
}

export async function writeSourceDocument(sourceDocument, outputPath) {
    const resolvedOutputPath = resolve(outputPath);
    await mkdir(dirname(resolvedOutputPath), { recursive: true });
    await writeFile(`${resolvedOutputPath}.tmp`, JSON.stringify(sourceDocument, null, 2));
    await rename(`${resolvedOutputPath}.tmp`, resolvedOutputPath);
    return resolvedOutputPath;
}

export async function writeLatestPointer({ inputPath, stem, version, sourcePath, xmindPath }) {
    const pointerPath = deriveLatestPointerPath(inputPath, stem);
    const payload = {
        stem: stem ?? parseVersionInfo(inputPath).baseStem,
        latestVersion: version ?? getVersionNumber(sourcePath ?? xmindPath) ?? 1,
        latestSourcePath: sourcePath ? resolve(sourcePath) : null,
        latestXmindPath: xmindPath ? resolve(xmindPath) : null,
        updatedAt: new Date().toISOString(),
    };
    await writeSourceDocument(payload, pointerPath);
    return pointerPath;
}

export function countTopics(topic) {
    if (!topic) return 0;
    const childList = Array.isArray(topic.children)
        ? topic.children
        : [
            ...(topic.children?.attached ?? []),
            ...(topic.children?.detached ?? []),
            ...(topic.children?.callout ?? []),
        ];
    return 1 + childList.reduce((sum, child) => sum + countTopics(child), 0);
}

export function collectTitles(topic, output = []) {
    if (!topic) return output;
    output.push(topic.title);
    const childList = Array.isArray(topic.children)
        ? topic.children
        : [
            ...(topic.children?.attached ?? []),
            ...(topic.children?.detached ?? []),
            ...(topic.children?.callout ?? []),
        ];
    for (const child of childList) collectTitles(child, output);
    return output;
}

export async function listZipEntries(filePath) {
    const { stdout } = await execFileAsync('unzip', ['-l', resolve(filePath)], {
        maxBuffer: 32 * 1024 * 1024,
    });
    return stdout;
}
