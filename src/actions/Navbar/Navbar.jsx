export const PUSH_BREADCRUMB = 'PUSH_BREADCRUMB'
export const POP_BREADCRUMB = 'POP_BREADCRUMB'

export function pushBreadcrumb(key, content, href) {
    return {
        type: PUSH_BREADCRUMB,
        key: key,
        content: content,
        href: href,
    }
}

export function popBreadcrumb(key) {
    return {
        type: POP_BREADCRUMB,
        key: key,
    }
}