# Django REST Framework Architectural Guidelines & Standardized Unified CRUD Pattern

This project enforces a standardized, unified CRUD architectural pattern using a single `APIView` per domain resource rather than fragmented generic class views (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`).

---

## 🏛 Architectural Pattern Specifications

### 1. Class-Based Encapsulation
* Every domain model `<ModelName>` is encapsulated inside a single class named `<ModelName>View(APIView)` extending `BaseUnifiedAPIView` (or `APIView`).
* Permission classes are declared per view (defaulting to `permission_classes = [IsAuthenticatedOrReadOnly]`, or `[AllowAny]` for public submit actions).

### 2. Unified Method Signatures & Object Resolution
Every view method supports resolving the target record via URL kwargs (`pk`, `slug`, `id`) or payload data (`id = request.data.get('id')`):
```python
def get_object(self, pk=None, slug=None, request_data=None):
    # Resolves target object by pk, slug, or request_data/query_params ('id' or 'pk')
```

### 3. HTTP Verb Responsibilities

#### `get(self, request, pk=None, slug=None, *args, **kwargs)`
* **Detail Retrieval:** If `pk`, `slug`, or query parameter `id`/`slug` is provided, return that single serialized instance (`HTTP_200_OK`), or `404` if not found.
* **List Retrieval:** If no identifier is given, return all items in the queryset (`many=True`).

#### `post(self, request, *args, **kwargs)`
* Extracts and validates payload fields.
* **Foreign Keys & Media Resolution:** Pre-processes payload data using `prepare_payload_data()`. Accepts raw integer IDs, stringified integers, or nested objects `{ "id": ... }` for both `<field>_id` and `<field>`.
* **ManyToMany / Categories:** Accepts list of IDs or instances for `<rel>_ids` and `<rel>`.
* **Auto-Slug Generation:** Automatically generates slugs via `slugify()` if the target model features a `slug` field and none was provided.
* Saves and returns the serialized record with `HTTP_201_CREATED`.

#### `put(self, request, pk=None, slug=None, *args, **kwargs)` & `patch(...)`
* Resolves the target record using `get_object()`.
* Updates fields provided in `request.data`.
* **Clearing Relational Fields:** Explicitly handles clearing relationships when fields are passed as `None` or `null`.
* Saves instance and returns serialized record with `HTTP_200_OK`.

#### `delete(self, request, pk=None, slug=None, *args, **kwargs)`
* Resolves target record.
* Checks object-level permissions (`self.check_object_permissions(request, obj)`).
* Deletes the record and returns `HTTP_204_NO_CONTENT` (or prevents deletion for singleton entities like `CompanyInfo`).

---

## 🛣 Standard URL Routing Pattern

Single view class handles all list, detail, and slug routes:

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
