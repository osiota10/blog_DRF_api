# Future Task: CKEditor 5 Media Library Picker Integration

This reference document outlines the plan and implementation steps for integrating a **Media Library Picker** into CKEditor 5 for frontend applications.

---

## 🎯 Goal
Allow users editing rich text content in CKEditor 5 to browse, search, and select existing images/assets from the `media_library` backend API (`MediaAsset`) instead of relying solely on fresh file uploads or manual external URL inputs.

---

## 📡 1. Backend API Endpoints Available

The `media_library` app provides endpoints for fetching assets:

* **List All Media Assets**: `GET /media-library/assets/`
* **Filter Images Only**: `GET /media-library/assets/?media_type=image`
* **Search Assets**: `GET /media-library/assets/?search=banner`

### Sample Response:
```json
[
  {
    "id": 14,
    "title": "hero_banner.png",
    "alt_text": "Hero Banner Image",
    "caption": "Sample banner for homepage",
    "media_type": "image",
    "url": "https://res.cloudinary.com/your-cloud/image/upload/v12345/media_library/hero_banner.png",
    "thumbnail_url": "https://res.cloudinary.com/your-cloud/image/upload/c_fill,f_auto,q_auto,w_300/v12345/media_library/hero_banner.png",
    "uploaded_at": "2026-08-25T22:00:00Z"
  }
]
```

---

## 🛠 2. Frontend CKEditor 5 Plugin & Modal Integration

### A. Register Custom Toolbar Button
Add a custom toolbar button in CKEditor 5 that triggers a modal component:

```javascript
import { ButtonView } from '@ckeditor/ckeditor5-ui';

editor.ui.componentFactory.add('mediaLibraryPicker', locale => {
    const view = new ButtonView(locale);

    view.set({
        label: 'Insert from Media Library',
        icon: '<svg>...</svg>', // Media library icon SVG
        tooltip: true
    });

    view.on('execute', () => {
        // Trigger Media Library Modal UI
        openMediaLibraryModal((selectedAsset) => {
            // Insert selected image into CKEditor 5 content
            editor.model.change(writer => {
                const imageElement = writer.createElement('imageBlock', {
                    src: selectedAsset.url,
                    alt: selectedAsset.alt_text || selectedAsset.title
                });
                editor.model.insertContent(imageElement, editor.model.document.selection);
            });
        });
    });

    return view;
});
```

---

## 🏷 3. Preserving `data-media-id` Attributes

To preserve `data-media-id="14"` or custom attributes on `<img>` tags inserted into CKEditor 5:

```javascript
ClassicEditor.create(document.querySelector('#editor'), {
    htmlSupport: {
        allow: [
            {
                name: 'img',
                attributes: {
                    'data-media-id': true,
                    'alt': true
                }
            }
        ]
    }
});
```

---

## 📋 Steps to Implement when Scheduled
1. Build a React / Vue / JS modal component connected to `GET /media-library/assets/?media_type=image`.
2. Register the `mediaLibraryPicker` button in the CKEditor 5 toolbar configuration.
3. Test inserting selected assets and verifying saved HTML post content.
