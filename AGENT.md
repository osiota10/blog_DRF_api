# Django REST Framework Architectural Guidelines & Standardized APIView Pattern

This project enforces an explicit, clean, and maintainable CRUD pattern using a single, self-contained `APIView` per resource without abstract metaclass introspection, dynamic schema scrapers, or magic helper wrappers.

---

## 🏛 Rules for Each View Class

### 1. Direct Inheritance & Permissions
* Every view class `<ModelName>View` inherits directly from `rest_framework.views.APIView`.
* Permission classes are set per class (defaulting to `permission_classes = [IsAuthenticatedOrReadOnly]`, or `AllowAny` for public submissions like `ContactFormView` / `EmailSubcriptionView`).

### 2. Explicit Lookup Resolution (`get_object`)
* Each class implements an explicit `get_object(self, pk=None, slug=None, request_data=None)` method.
* Resolves instances using `pk`, `slug`, or fallback payload fields (`request.data.get('id')` / `request.data.get('pk')`).
* Returns `None` if not found (view methods return `HTTP_404_NOT_FOUND`).

### 3. HTTP Verb Implementation

#### `get(self, request, pk=None, slug=None, *args, **kwargs)`
* **Detail:** If `pk`, `slug`, or an ID/slug query parameter is present, return that single serialized instance (`HTTP_200_OK`).
* **List:** Otherwise, return all records ordered by `-id` (`many=True`).

#### `post(self, request, *args, **kwargs)`
* Extracts fields explicitly from `request.data`.
* **Foreign Media Asset Resolution:** Resolves both `<field>_id` and `<field>`. Extracts integer IDs from raw integers, stringified integers, or nested objects `{ "id": ... }`.
* **ManyToMany Relationships:** Resolves list of IDs or instances for `<rel>_ids` and `<rel>`.
* **Auto-Slug:** Auto-generates `slug` via `slugify()` if model has a slug field and none was provided.
* Saves and returns serialized result with `HTTP_201_CREATED`.

#### `put(self, request, pk=None, slug=None, *args, **kwargs)` & `patch(...)`
* Retrieves instance via `self.get_object(...)`.
* Updates fields present in `request.data`.
* Supports clearing media (`None`) or re-assigning new media asset IDs.
* Saves instance and returns updated data with `HTTP_200_OK`.

#### `delete(self, request, pk=None, slug=None, *args, **kwargs)`
* Retrieves instance via `self.get_object(...)`.
* Calls `.delete()` and returns `HTTP_204_NO_CONTENT` (or returns `HTTP_400_BAD_REQUEST` for singleton instances like `CompanyInfo`).

---

## 🛣 Standard URL Routing Pattern

```python
urlpatterns = [
    path('<plural>', <ModelName>View.as_view(), name='<singular>-list-create'),
    path('<plural>/', <ModelName>View.as_view(), name='<singular>-list-create-slash'),
    path('<plural>/<int:pk>', <ModelName>View.as_view(), name='<singular>-detail'),
    path('<plural>/<int:pk>/', <ModelName>View.as_view(), name='<singular>-detail-slash'),
    path('<plural>/<slug:slug>', <ModelName>View.as_view(), name='<singular>-detail-slug'),
    path('<plural>/<slug:slug>/', <ModelName>View.as_view(), name='<singular>-detail-slug-slash'),
]
```
