<?php

declare(strict_types=1);

namespace CalServer\Cms;

/**
 * Lightweight page representation exposing only metadata used for runtime selection.
 */
class Page
{
    public function __construct(
        public readonly ?string $type = null,
        public readonly ?string $contentSource = null,
        public readonly ?string $namespace = null,
    ) {
    }
}

/**
 * Decide which runtime pipeline a page belongs to using explicit metadata only.
 *
 * Defaults to LegacyMarketing when metadata is ambiguous to avoid leaking
 * marketing behavior into CmsBuilder handling.
 */
function determinePageRuntimeType(Page $page): PageRuntimeType
{
    if ($page->type === 'system' || $page->namespace === 'system') {
        return PageRuntimeType::System;
    }

    if ($page->type === 'cms_builder' || $page->contentSource === 'cms_builder') {
        return PageRuntimeType::CmsBuilder;
    }

    return PageRuntimeType::LegacyMarketing;
}
