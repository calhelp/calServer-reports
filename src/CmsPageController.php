<?php

declare(strict_types=1);

namespace CalServer\Cms;

/**
 * Controller stub that records the runtime type before any downstream loading.
 */
final class CmsPageController
{
    public function render(Page $page): void
    {
        $runtimeType = determinePageRuntimeType($page);

        $content = $this->loadPageContent($page, $runtimeType);
        $modules = $this->loadPageModules($page, $runtimeType);

        $this->renderView($runtimeType, $content, $modules);
    }

    private function loadPageContent(Page $page, PageRuntimeType $runtimeType): array
    {
        // Placeholder: actual loader wiring intentionally omitted to keep behavior unchanged.
        return ['page' => $page, 'runtime' => $runtimeType];
    }

    private function loadPageModules(Page $page, PageRuntimeType $runtimeType): array
    {
        // Placeholder: actual module resolution intentionally omitted to keep behavior unchanged.
        return ['page' => $page, 'runtime' => $runtimeType];
    }

    private function renderView(PageRuntimeType $runtimeType, array $content, array $modules): void
    {
        // Placeholder: rendering intentionally omitted; runtime type is now available to the flow.
    }
}
