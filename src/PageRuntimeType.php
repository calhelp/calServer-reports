<?php

declare(strict_types=1);

namespace CalServer\Cms;

/**
 * Runtime classification for CMS-facing pages.
 *
 * This explicit runtime type prevents LegacyMarketingPage behavior
 * from leaking into CmsBuilderPage handling and vice versa.
 */
enum PageRuntimeType: string
{
    case LegacyMarketing = 'legacy_marketing';
    case CmsBuilder = 'cms_builder';
    case System = 'system';
}
