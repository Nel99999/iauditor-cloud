# 🎯 V1.0 & V2.0 OPERATIONAL PLATFORM - COMPLETE IMPLEMENTATION PLAN

**Strategic Roadmap** | **January 2025 - December 2025** | **Systematic Build**

---

# 📋 LAUNCH V1 - CORE OPERATIONAL PLATFORM

**Target Timeline:** 16-20 weeks (4-5 months)  
**Modules:** 18 modules across 9 domains  
**Goal:** Production-ready operational excellence platform

---

## 🏗️ PHASE 1: FOUNDATION & UNIFIED SERVICES (Weeks 1-3)

### **Objective:** 
Build the shared infrastructure layer that ALL modules will use. This prevents duplication and ensures consistency.

---

### **1.1 UNIFIED SERVICES LAYER**

#### **A. Attachment Service (Universal File Management)**

**Purpose:** Single service for all file uploads (photos, PDFs, videos, documents)

**Technical Specifications:**

**Backend: `/backend/shared_services/attachment_service.py`**
```python
class AttachmentService:
    """Universal attachment handler using GridFS"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.fs = AsyncIOMotorGridFSBucket(db)
    
    async def upload_file(
        self,
        file: UploadFile,
        entity_type: str,  # 'inspection', 'task', 'incident', etc.
        entity_id: str,
        uploaded_by: str,
        organization_id: str,
        metadata: dict = {}
    ) -> dict:
        """Upload file and create attachment record"""
        
        # Validate file size (max 50MB)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise ValueError("File too large (max 50MB)")
        
        # Upload to GridFS
        file_id = await self.fs.upload_from_stream(
            file.filename,
            io.BytesIO(content),
            metadata={
                "content_type": file.content_type,
                "uploaded_by": uploaded_by,
                "organization_id": organization_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                **metadata
            }
        )
        
        # Create attachment record
        attachment = {
            "id": str(uuid.uuid4()),
            "file_id": str(file_id),
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(content),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "uploaded_by": uploaded_by,
            "organization_id": organization_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.attachments.insert_one(attachment)
        
        return {
            "id": attachment["id"],
            "file_id": str(file_id),
            "filename": file.filename,
            "url": f"/api/attachments/{attachment['id']}"
        }
    
    async def get_attachments(
        self,
        entity_type: str,
        entity_id: str
    ) -> list:
        """Get all attachments for an entity"""
        attachments = await self.db.attachments.find({
            "entity_type": entity_type,
            "entity_id": entity_id
        }, {"_id": 0}).to_list(length=None)
        
        return attachments
    
    async def delete_attachment(
        self,
        attachment_id: str,
        user_id: str
    ) -> bool:
        """Delete attachment (soft delete or full delete)"""
        attachment = await self.db.attachments.find_one({"id": attachment_id})
        
        if not attachment:
            return False
        
        # Delete from GridFS
        await self.fs.delete(ObjectId(attachment["file_id"]))
        
        # Delete record
        await self.db.attachments.delete_one({"id": attachment_id})
        
        return True
```

**API Endpoints:**
```python
# /backend/attachment_routes.py

@router.post("/attachments/upload")
async def upload_attachment(
    file: UploadFile,
    entity_type: str,
    entity_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Upload file and attach to entity"""
    service = AttachmentService(db)
    return await service.upload_file(
        file, entity_type, entity_id,
        current_user["id"], current_user["organization_id"]
    )

@router.get("/attachments/{entity_type}/{entity_id}")
async def get_attachments(
    entity_type: str,
    entity_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all attachments for entity"""
    service = AttachmentService(db)
    return await service.get_attachments(entity_type, entity_id)

@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Download/stream attachment file"""
    service = AttachmentService(db)
    return await service.download_file(attachment_id)

@router.delete("/attachments/{attachment_id}")
async def delete_attachment(
    attachment_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete attachment"""
    service = AttachmentService(db)
    return await service.delete_attachment(attachment_id, current_user["id"])
```

**Frontend Component: `/frontend/src/components/shared/AttachmentManager.tsx`**
```typescript
interface AttachmentManagerProps {
  entityType: string;  // 'inspection', 'task', etc.
  entityId: string;
  readOnly?: boolean;
}

const AttachmentManager: React.FC<AttachmentManagerProps> = ({
  entityType,
  entityId,
  readOnly = false
}) => {
  const [attachments, setAttachments] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('entity_type', entityType);
    formData.append('entity_id', entityId);
    
    const response = await axios.post('/api/attachments/upload', formData);
    loadAttachments();
  };
  
  const handleDelete = async (attachmentId: string) => {
    await axios.delete(`/api/attachments/${attachmentId}`);
    loadAttachments();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Attachments ({attachments.length})</CardTitle>
      </CardHeader>
      <CardContent>
        {!readOnly && (
          <div className="border-dashed border-2 p-4 text-center">
            <input type="file" onChange={(e) => handleUpload(e.target.files[0])} />
            <p>Drag & drop or click to upload</p>
          </div>
        )}
        
        <div className="grid grid-cols-3 gap-4 mt-4">
          {attachments.map(att => (
            <div key={att.id} className="border rounded p-2">
              <img src={`/api/attachments/${att.id}/download`} />
              <p className="text-sm">{att.filename}</p>
              {!readOnly && (
                <Button onClick={() => handleDelete(att.id)}>Delete</Button>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
```

**Database Schema:**
```javascript
attachments {
  id: uuid,
  file_id: ObjectId (GridFS reference),
  filename: string,
  content_type: string,
  size_bytes: number,
  entity_type: string (indexed),
  entity_id: string (indexed),
  uploaded_by: uuid (user_id),
  organization_id: uuid (indexed),
  tags: array,
  created_at: datetime
}

// GridFS collections (auto-created):
fs.files {
  _id: ObjectId,
  length: number,
  chunkSize: number,
  uploadDate: datetime,
  filename: string,
  metadata: object
}

fs.chunks {
  _id: ObjectId,
  files_id: ObjectId,
  n: number,
  data: binary
}
```

**Effort:** 3-4 days  
**Dependencies:** None  
**Priority:** P0 (blocking)

---

#### **B. Comment Service (Universal Discussions)**

**Purpose:** Threaded comments on any work item with @mentions

**Backend: `/backend/shared_services/comment_service.py`**
```python
class CommentService:
    """Universal comment/discussion handler"""
    
    async def create_comment(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str,
        organization_id: str,
        content: str,
        parent_comment_id: str = None,
        mentions: list = []
    ) -> dict:
        """Create comment and send notifications to mentioned users"""
        
        comment = {
            "id": str(uuid.uuid4()),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "organization_id": organization_id,
            "content": content,
            "parent_id": parent_comment_id,  # For threading
            "mentions": mentions,  # List of user_ids
            "edited": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.comments.insert_one(comment)
        
        # Send notifications to mentioned users
        for mentioned_user_id in mentions:
            await self.notification_service.create_notification(
                user_id=mentioned_user_id,
                type="mention",
                title=f"You were mentioned in a comment",
                message=content[:100],
                link=f"/{entity_type}/{entity_id}",
                data={"comment_id": comment["id"]}
            )
        
        return comment
    
    async def get_comments(
        self,
        entity_type: str,
        entity_id: str
    ) -> list:
        """Get all comments for entity (nested threading)"""
        comments = await self.db.comments.find({
            "entity_type": entity_type,
            "entity_id": entity_id
        }, {"_id": 0}).sort("created_at", 1).to_list(length=None)
        
        # Populate user details
        for comment in comments:
            user = await self.db.users.find_one({"id": comment["user_id"]})
            if user:
                comment["user_name"] = user["name"]
                comment["user_picture"] = user.get("picture")
        
        # Build threaded structure (parent → replies)
        threaded = self._build_thread_tree(comments)
        
        return threaded
    
    def _build_thread_tree(self, comments: list) -> list:
        """Build nested comment structure"""
        comment_map = {c["id"]: {**c, "replies": []} for c in comments}
        root_comments = []
        
        for comment in comments:
            if comment.get("parent_id"):
                parent = comment_map.get(comment["parent_id"])
                if parent:
                    parent["replies"].append(comment_map[comment["id"]])
            else:
                root_comments.append(comment_map[comment["id"]])
        
        return root_comments
```

**API Endpoints:**
```python
# /backend/comment_routes.py

@router.post("/comments")
async def create_comment(
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create comment on any entity"""
    service = CommentService(db)
    return await service.create_comment(
        comment_data.entity_type,
        comment_data.entity_id,
        current_user["id"],
        current_user["organization_id"],
        comment_data.content,
        comment_data.parent_id,
        comment_data.mentions
    )

@router.get("/comments/{entity_type}/{entity_id}")
async def get_comments(
    entity_type: str,
    entity_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all comments for entity (threaded)"""
    service = CommentService(db)
    return await service.get_comments(entity_type, entity_id)

@router.put("/comments/{comment_id}")
async def update_comment(
    comment_id: str,
    content: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Edit comment (only by author)"""
    service = CommentService(db)
    return await service.update_comment(comment_id, content, current_user["id"])

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete comment (only by author or admin)"""
    service = CommentService(db)
    return await service.delete_comment(comment_id, current_user["id"])
```

**Frontend Component: `/frontend/src/components/shared/CommentThread.tsx`**
```typescript
interface CommentThreadProps {
  entityType: string;
  entityId: string;
  readOnly?: boolean;
}

const CommentThread: React.FC<CommentThreadProps> = ({
  entityType,
  entityId,
  readOnly = false
}) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState(null);

  const handleSubmit = async () => {
    await axios.post('/api/comments', {
      entity_type: entityType,
      entity_id: entityId,
      content: newComment,
      parent_id: replyingTo?.id,
      mentions: extractMentions(newComment)
    });
    setNewComment('');
    setReplyingTo(null);
    loadComments();
  };

  const renderComment = (comment, level = 0) => (
    <div key={comment.id} style={{ marginLeft: level * 20 }}>
      <Card className="mb-2">
        <CardContent className="p-3">
          <div className="flex gap-3">
            <Avatar>
              <AvatarImage src={comment.user_picture} />
              <AvatarFallback>{comment.user_name[0]}</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex justify-between">
                <span className="font-semibold">{comment.user_name}</span>
                <span className="text-xs text-gray-500">
                  {formatDate(comment.created_at)}
                </span>
              </div>
              <p className="mt-1">{comment.content}</p>
              {!readOnly && (
                <Button size="sm" variant="ghost" onClick={() => setReplyingTo(comment)}>
                  Reply
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Nested replies */}
      {comment.replies?.map(reply => renderComment(reply, level + 1))}
    </div>
  );

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">
        Comments ({comments.length})
      </h3>
      
      {!readOnly && (
        <div>
          {replyingTo && (
            <div className="text-sm text-gray-600 mb-2">
              Replying to {replyingTo.user_name}
              <Button size="sm" onClick={() => setReplyingTo(null)}>Cancel</Button>
            </div>
          )}
          <Textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a comment... (use @username to mention)"
            rows={3}
          />
          <Button onClick={handleSubmit} className="mt-2">
            Post Comment
          </Button>
        </div>
      )}
      
      <div className="space-y-2">
        {comments.map(comment => renderComment(comment))}
      </div>
    </div>
  );
};
```

**Database Schema:**
```javascript
comments {
  id: uuid,
  entity_type: string (indexed),
  entity_id: string (indexed),
  user_id: uuid,
  organization_id: uuid (indexed),
  content: text,
  parent_id: uuid (for threading),
  mentions: array[uuid] (user_ids mentioned),
  edited: boolean,
  created_at: datetime,
  updated_at: datetime
}

// Indexes:
db.comments.createIndex({ entity_type: 1, entity_id: 1 })
db.comments.createIndex({ organization_id: 1, created_at: -1 })
```

**Effort:** 3-4 days  
**Dependencies:** Notification service

---

#### **C. Notification Service (Multi-Channel Alerts)**

**Purpose:** Unified notification system (in-app, email, SMS, push)

**Backend: `/backend/shared_services/notification_service.py`**
```python
class NotificationService:
    """Universal notification handler"""
    
    async def create_notification(
        self,
        user_id: str,
        type: str,  # 'mention', 'assignment', 'approval', 'alert', 'deadline'
        title: str,
        message: str,
        link: str = None,
        data: dict = {},
        priority: str = 'normal',  # 'low', 'normal', 'high', 'urgent'
        channels: list = ['in_app']  # 'in_app', 'email', 'sms', 'push'
    ):
        """Create and send notification"""
        
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": type,
            "title": title,
            "message": message,
            "link": link,
            "data": data,
            "priority": priority,
            "channels": channels,
            "read": False,
            "read_at": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.notifications.insert_one(notification)
        
        # Send via requested channels
        if 'email' in channels:
            await self._send_email(user_id, title, message, link)
        
        if 'sms' in channels and priority in ['high', 'urgent']:
            await self._send_sms(user_id, message)
        
        if 'push' in channels:
            await self._send_push(user_id, title, message, data)
        
        return notification
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ):
        """Get notifications for user"""
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
        
        notifications = await self.db.notifications.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return notifications
    
    async def mark_as_read(self, notification_id: str):
        """Mark notification as read"""
        await self.db.notifications.update_one(
            {"id": notification_id},
            {"$set": {
                "read": True,
                "read_at": datetime.now(timezone.utc).isoformat()
            }}
        )
```

**API Endpoints:**
```python
@router.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's notifications"""
    service = NotificationService(db)
    return await service.get_user_notifications(
        current_user["id"], unread_only, limit
    )

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark notification as read"""
    service = NotificationService(db)
    return await service.mark_as_read(notification_id)

@router.put("/notifications/mark-all-read")
async def mark_all_read(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark all notifications as read"""
    service = NotificationService(db)
    return await service.mark_all_read(current_user["id"])
```

**Frontend Component: Already exists as NotificationCenter**
- Enhance with real-time updates (WebSocket or polling)
- Add notification preferences (per module, per channel)

**Database Schema:**
```javascript
notifications {
  id: uuid,
  user_id: uuid (indexed),
  type: string,
  title: string,
  message: text,
  link: string,
  data: object,
  priority: string,
  channels: array,
  read: boolean (indexed),
  read_at: datetime,
  created_at: datetime
}

notification_preferences {
  id: uuid,
  user_id: uuid,
  module: string,
  notification_type: string,
  in_app: boolean,
  email: boolean,
  sms: boolean,
  push: boolean,
  do_not_disturb_start: time,
  do_not_disturb_end: time
}
```

**Effort:** 2-3 days  
**Dependencies:** Email service (already exists)

---

#### **D. Activity/Audit Service (Universal Audit Trail)**

**Purpose:** Track all changes to all entities

**Backend: `/backend/shared_services/activity_service.py`**
```python
class ActivityService:
    """Universal activity logging"""
    
    async def log_activity(
        self,
        entity_type: str,
        entity_id: str,
        action: str,  # 'created', 'updated', 'deleted', 'status_changed', 'assigned', 'completed'
        user_id: str,
        organization_id: str,
        details: dict = {},
        changes: dict = {}  # {field: {old: value, new: value}}
    ):
        """Log activity/change"""
        
        activity = {
            "id": str(uuid.uuid4()),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "user_id": user_id,
            "organization_id": organization_id,
            "details": details,
            "changes": changes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.activities.insert_one(activity)
        
        return activity
    
    async def get_entity_activity(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 100
    ):
        """Get activity timeline for entity"""
        activities = await self.db.activities.find({
            "entity_type": entity_type,
            "entity_id": entity_id
        }, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
        
        # Populate user names
        for activity in activities:
            user = await self.db.users.find_one({"id": activity["user_id"]})
            if user:
                activity["user_name"] = user["name"]
        
        return activities
```

**Frontend Component: `/frontend/src/components/shared/ActivityTimeline.tsx`**
```typescript
const ActivityTimeline: React.FC<{entityType: string, entityId: string}> = ({
  entityType, entityId
}) => {
  const [activities, setActivities] = useState([]);

  const getActivityIcon = (action) => {
    const icons = {
      created: <Plus />,
      updated: <Edit />,
      status_changed: <RefreshCw />,
      assigned: <UserPlus />,
      completed: <CheckCircle />,
      deleted: <Trash2 />
    };
    return icons[action] || <Activity />;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {activities.map(activity => (
            <div key={activity.id} className="flex gap-3 border-l-2 pl-3">
              {getActivityIcon(activity.action)}
              <div className="flex-1">
                <p>
                  <strong>{activity.user_name}</strong> {activity.action} 
                </p>
                {activity.changes && Object.keys(activity.changes).length > 0 && (
                  <div className="text-sm text-gray-600">
                    {Object.entries(activity.changes).map(([field, change]) => (
                      <div key={field}>
                        {field}: {change.old} → {change.new}
                      </div>
                    ))}
                  </div>
                )}
                <span className="text-xs text-gray-500">
                  {formatDate(activity.timestamp)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
```

**Effort:** 2 days  
**Dependencies:** None

---

#### **E. Tag Service (Flexible Categorization)**

**Purpose:** Universal tagging for all entities

**Backend: Simple, integrated into entities**
```python
# Add to all work item models:
tags: list[str] = []  # ['safety', 'critical', 'Q1-2025']

# Search by tag:
items = await db.inspections.find({"tags": {"$in": ["safety"]}})

# Tag autocomplete endpoint:
@router.get("/tags/autocomplete")
async def get_tag_suggestions(
    entity_type: str,
    query: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get tag suggestions based on existing tags"""
    collection_name = f"{entity_type}_executions"  # or templates
    
    # Aggregate all unique tags
    pipeline = [
        {"$match": {"organization_id": current_user["organization_id"]}},
        {"$unwind": "$tags"},
        {"$match": {"tags": {"$regex": f"^{query}", "$options": "i"}}},
        {"$group": {"_id": "$tags"}},
        {"$limit": 10}
    ]
    
    results = await db[collection_name].aggregate(pipeline).to_list(length=10)
    return [r["_id"] for r in results]
```

**Frontend: Tag input component with autocomplete**

**Effort:** 1 day

---

### **1.2 BASE DATA MODEL ENHANCEMENTS**

**Add to ALL Work Items (Inspections, Checklists, Tasks, Projects, Incidents):**

```python
# Base Work Item Model (inherit this)
class BaseWorkItem(BaseModel):
    # Core Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    
    # Org Hierarchy Integration (NEW)
    unit_id: Optional[str] = None  # Which org unit owns this
    scope: str = "organization"  # "organization", "unit", "team"
    visibility: str = "organization"  # Who can see this
    
    # Assignment (NEW/ENHANCED)
    created_by: str
    assigned_to: Optional[str] = None  # User who must complete
    assigned_by: Optional[str] = None  # User who assigned
    
    # Status & Lifecycle
    status: str  # Module-specific statuses
    priority: str = "medium"  # "low", "medium", "high", "urgent"
    
    # Dates (ENHANCED)
    created_at: datetime
    started_at: Optional[datetime] = None
    due_date: Optional[datetime] = None  # NEW
    completed_at: Optional[datetime] = None
    updated_at: datetime
    
    # Asset Linking (NEW - CRITICAL)
    asset_id: Optional[str] = None  # Primary asset
    related_asset_ids: list[str] = []  # Multiple assets
    
    # Workflow Integration (NEW)
    workflow_id: Optional[str] = None  # Linked approval workflow
    approval_required: bool = False
    approval_status: Optional[str] = None  # "pending", "approved", "rejected"
    
    # Categorization
    tags: list[str] = []
    category: Optional[str] = None
    
    # Collaboration (counts, actual data in separate collections)
    comment_count: int = 0
    attachment_count: int = 0
    follower_ids: list[str] = []  # Users following this item
```

**Migration Script:**
```python
# /backend/migrations/add_base_fields.py

async def migrate_work_items():
    """Add new base fields to existing work items"""
    
    collections = [
        "inspection_executions",
        "checklist_executions",
        "tasks"
    ]
    
    for collection_name in collections:
        collection = db[collection_name]
        
        # Add missing fields to all documents
        await collection.update_many(
            {},
            {"$set": {
                "unit_id": None,
                "scope": "organization",
                "assigned_to": None,
                "assigned_by": None,
                "due_date": None,
                "asset_id": None,
                "related_asset_ids": [],
                "workflow_id": None,
                "approval_required": False,
                "tags": [],
                "comment_count": 0,
                "attachment_count": 0,
                "follower_ids": []
            }}
        )
        
        print(f"✅ Migrated {collection_name}")
```

**Effort:** 2 days (including testing)

---

### **WEEK 1-2 DELIVERABLES:**
✅ Attachment Service (universal file uploads)  
✅ Comment Service (threaded discussions)  
✅ Notification Service (multi-channel)  
✅ Activity Service (audit trails)  
✅ Tag Service (flexible categorization)  
✅ Base data model updated (all work items)

**Total Effort:** 12-14 days  
**Team:** 1 backend + 1 frontend developer

---

### **1.3 ENHANCED RBAC (Weeks 2-3)**

**Goal:** Add missing permission checks, implement scope-based access

**Backend Changes:**

**A. Add Missing Permissions:**
```python
# In permission_routes.py initialize_permissions()

NEW_PERMISSIONS = [
    # Inspection permissions (scope-based)
    {"resource_type": "inspection", "action": "create", "scope": "unit"},
    {"resource_type": "inspection", "action": "read", "scope": "unit"},
    {"resource_type": "inspection", "action": "read", "scope": "children"},
    {"resource_type": "inspection", "action": "assign", "scope": "unit"},
    {"resource_type": "inspection", "action": "approve", "scope": "unit"},
    
    # Checklist permissions
    {"resource_type": "checklist", "action": "create", "scope": "unit"},
    {"resource_type": "checklist", "action": "read", "scope": "unit"},
    {"resource_type": "checklist", "action": "assign", "scope": "unit"},
    
    # Task permissions
    {"resource_type": "task", "action": "read", "scope": "unit"},
    {"resource_type": "task", "action": "read", "scope": "children"},
    {"resource_type": "task", "action": "assign", "scope": "unit"},
    
    # Asset permissions (NEW module)
    {"resource_type": "asset", "action": "create", "scope": "organization"},
    {"resource_type": "asset", "action": "read", "scope": "organization"},
    {"resource_type": "asset", "action": "read", "scope": "unit"},
    {"resource_type": "asset", "action": "read", "scope": "children"},
    {"resource_type": "asset", "action": "update", "scope": "organization"},
    {"resource_type": "asset", "action": "delete", "scope": "organization"},
    
    # Work order permissions (NEW)
    {"resource_type": "work_order", "action": "create", "scope": "unit"},
    {"resource_type": "work_order", "action": "read", "scope": "own"},
    {"resource_type": "work_order", "action": "read", "scope": "unit"},
    {"resource_type": "work_order", "action": "assign", "scope": "unit"},
    {"resource_type": "work_order", "action": "approve", "scope": "unit"},
    
    # ... (continue for all modules)
]
```

**B. Scope-Based Filtering:**
```python
# /backend/shared_services/scope_service.py

class ScopeService:
    """Handle org hierarchy-based access filtering"""
    
    async def get_accessible_unit_ids(
        self,
        user: dict,
        scope: str
    ) -> list[str]:
        """Get unit IDs user can access based on scope"""
        
        user_unit_id = user.get("unit_id")
        
        if scope == "own":
            return []  # Only items directly assigned to user
        
        elif scope == "unit":
            return [user_unit_id] if user_unit_id else []
        
        elif scope == "children":
            # Get user's unit + all child units
            if not user_unit_id:
                return []
            
            units = await self._get_unit_hierarchy(user_unit_id)
            return [u["id"] for u in units]
        
        elif scope == "organization":
            # All units in organization
            units = await self.db.organization_units.find({
                "organization_id": user["organization_id"]
            }, {"_id": 0, "id": 1}).to_list(length=None)
            
            return [u["id"] for u in units]
        
        return []
    
    async def _get_unit_hierarchy(self, unit_id: str) -> list:
        """Get unit and all child units recursively"""
        units = []
        
        # Get this unit
        unit = await self.db.organization_units.find_one({"id": unit_id})
        if unit:
            units.append(unit)
            
            # Get children
            children = await self.db.organization_units.find({
                "parent_id": unit_id
            }).to_list(length=None)
            
            for child in children:
                child_hierarchy = await self._get_unit_hierarchy(child["id"])
                units.extend(child_hierarchy)
        
        return units
    
    async def apply_scope_filter(
        self,
        query: dict,
        user: dict,
        permission_scope: str
    ) -> dict:
        """Apply scope filtering to MongoDB query"""
        
        if permission_scope == "own":
            # Only items assigned to this user
            query["assigned_to"] = user["id"]
        
        elif permission_scope in ["unit", "children"]:
            # Items in accessible units
            unit_ids = await self.get_accessible_unit_ids(user, permission_scope)
            if unit_ids:
                query["unit_id"] = {"$in": unit_ids}
        
        elif permission_scope == "organization":
            # Already filtered by organization_id (standard)
            pass
        
        return query
```

**Usage in Endpoints:**
```python
@router.get("/inspections/executions")
async def get_inspections(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get inspections with scope-based filtering"""
    
    # Check permission and get scope
    from permission_routes import get_user_permission_scope
    scope = await get_user_permission_scope(
        db, current_user["id"], "inspection", "read"
    )
    # Returns: "own", "unit", "children", "organization", or None
    
    if not scope:
        raise HTTPException(403, "No permission to read inspections")
    
    # Build base query
    query = {"organization_id": current_user["organization_id"]}
    if status:
        query["status"] = status
    
    # Apply scope filtering
    scope_service = ScopeService(db)
    query = await scope_service.apply_scope_filter(query, current_user, scope)
    
    # Execute query
    inspections = await db.inspection_executions.find(query).to_list(1000)
    
    return inspections
```

**Effort:** 4-5 days  
**Dependencies:** Permission system (exists)

---

### **WEEK 2-3 DELIVERABLES:**
✅ Scope-based access control  
✅ Missing permissions added  
✅ All endpoints enforce permissions  
✅ Hierarchical visibility working  

**Total Effort:** 4-5 days

---

## 🏗️ PHASE 2: ASSET MANAGEMENT FOUNDATION (Weeks 4-7)

### **Objective:**
Create the asset-centric foundation that all operations modules will link to.

---

### **2.1 ASSET REGISTER MODULE**

**Purpose:** Comprehensive asset database

**Data Model: `/backend/asset_models.py`**
```python
class Asset(BaseModel):
    """Core asset model"""
    model_config = ConfigDict(extra="ignore")
    
    # Identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_tag: str  # Unique identifier (barcode/QR code)
    name: str
    description: Optional[str] = None
    
    # Classification
    organization_id: str
    asset_type: str  # "equipment", "infrastructure", "vehicle", "it_asset", "safety_equipment", "tool"
    category: Optional[str] = None  # Industry-specific (pump, motor, HVAC, etc.)
    criticality: str = "C"  # "A" (critical), "B" (important), "C" (standard)
    
    # Location & Hierarchy
    unit_id: str  # Organizational unit
    location_details: Optional[str] = None  # Building, Floor, Room
    gps_coordinates: Optional[dict] = None  # {"lat": 0.0, "lng": 0.0}
    
    # Asset Hierarchy (parent-child)
    parent_asset_id: Optional[str] = None  # For subsystems
    has_children: bool = False
    
    # Technical Specifications
    make: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    year_manufactured: Optional[int] = None
    specifications: dict = {}  # Flexible specs (voltage, capacity, etc.)
    
    # Ownership
    owner_id: str  # Department/unit that owns it
    custodian_id: Optional[str] = None  # Person responsible
    
    # Financial
    purchase_date: Optional[datetime] = None
    purchase_cost: Optional[float] = None
    current_value: Optional[float] = None
    depreciation_rate: Optional[float] = None  # % per year
    salvage_value: Optional[float] = None
    
    # Lifecycle
    status: str = "operational"  # "operational", "maintenance", "down", "retired", "disposed"
    installation_date: Optional[datetime] = None
    commissioning_date: Optional[datetime] = None
    retirement_date: Optional[datetime] = None
    expected_life_years: Optional[int] = None
    
    # Maintenance
    maintenance_schedule: Optional[str] = None  # "weekly", "monthly", "quarterly", "annually"
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    pm_template_ids: list[str] = []  # Linked PM templates
    
    # Calibration (if applicable)
    requires_calibration: bool = False
    calibration_frequency_days: Optional[int] = None
    last_calibration_date: Optional[datetime] = None
    next_calibration_date: Optional[datetime] = None
    
    # Documentation
    manual_url: Optional[str] = None
    drawing_ids: list[str] = []  # Linked technical drawings
    warranty_expiry: Optional[datetime] = None
    
    # Performance Tracking
    total_downtime_hours: float = 0.0
    mtbf_hours: Optional[float] = None  # Mean Time Between Failures
    mttr_hours: Optional[float] = None  # Mean Time To Repair
    
    # Metadata
    tags: list[str] = []
    custom_fields: dict = {}  # Extensible
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

**API Endpoints: `/backend/asset_routes.py`**
```python
router = APIRouter(prefix="/assets", tags=["Assets"])

@router.post("", status_code=201)
async def create_asset(
    asset_data: AssetCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create new asset - Requires asset.create.organization"""
    # Permission check
    has_permission = await check_permission(
        db, current_user["id"], "asset", "create", "organization"
    )
    if not has_permission:
        raise HTTPException(403, "No permission to create assets")
    
    asset = Asset(
        organization_id=current_user["organization_id"],
        created_by=current_user["id"],
        **asset_data.dict()
    )
    
    await db.assets.insert_one(asset.dict())
    
    # Log activity
    await activity_service.log_activity(
        "asset", asset.id, "created", current_user["id"],
        current_user["organization_id"]
    )
    
    return asset

@router.get("")
async def list_assets(
    asset_type: Optional[str] = None,
    unit_id: Optional[str] = None,
    status: Optional[str] = None,
    criticality: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """List assets with filtering and scope-based access"""
    # Get permission scope
    scope = await get_user_permission_scope(
        db, current_user["id"], "asset", "read"
    )
    
    if not scope:
        raise HTTPException(403, "No permission to read assets")
    
    # Build query
    query = {"organization_id": current_user["organization_id"], "is_active": True}
    
    # Apply filters
    if asset_type:
        query["asset_type"] = asset_type
    if unit_id:
        query["unit_id"] = unit_id
    if status:
        query["status"] = status
    if criticality:
        query["criticality"] = criticality
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"asset_tag": {"$regex": search, "$options": "i"}},
            {"serial_number": {"$regex": search, "$options": "i"}}
        ]
    
    # Apply scope filtering
    scope_service = ScopeService(db)
    query = await scope_service.apply_scope_filter(query, current_user, scope)
    
    assets = await db.assets.find(query, {"_id": 0}).to_list(1000)
    
    return assets

@router.get("/{asset_id}")
async def get_asset(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get asset details"""
    asset = await db.assets.find_one({
        "id": asset_id,
        "organization_id": current_user["organization_id"]
    }, {"_id": 0})
    
    if not asset:
        raise HTTPException(404, "Asset not found")
    
    return asset

@router.put("/{asset_id}")
async def update_asset(
    asset_id: str,
    asset_data: AssetUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update asset - Requires asset.update.organization"""
    has_permission = await check_permission(
        db, current_user["id"], "asset", "update", "organization"
    )
    if not has_permission:
        raise HTTPException(403, "No permission to update assets")
    
    update_data = asset_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Track changes for activity log
    old_asset = await db.assets.find_one({"id": asset_id})
    changes = {
        k: {"old": old_asset.get(k), "new": v}
        for k, v in update_data.items()
        if old_asset.get(k) != v
    }
    
    await db.assets.update_one(
        {"id": asset_id},
        {"$set": update_data}
    )
    
    # Log activity
    await activity_service.log_activity(
        "asset", asset_id, "updated", current_user["id"],
        current_user["organization_id"], changes=changes
    )
    
    return await db.assets.find_one({"id": asset_id}, {"_id": 0})

@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Soft delete asset"""
    has_permission = await check_permission(
        db, current_user["id"], "asset", "delete", "organization"
    )
    if not has_permission:
        raise HTTPException(403, "No permission to delete assets")
    
    await db.assets.update_one(
        {"id": asset_id},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Asset deleted"}

@router.get("/{asset_id}/history")
async def get_asset_history(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get complete history of asset (all work orders, inspections, incidents)"""
    
    # Get all related work
    history = {
        "inspections": await db.inspection_executions.find({
            "asset_id": asset_id
        }).sort("started_at", -1).limit(50).to_list(50),
        
        "work_orders": await db.work_orders.find({
            "asset_id": asset_id
        }).sort("created_at", -1).limit(50).to_list(50),
        
        "incidents": await db.incidents.find({
            "asset_id": asset_id
        }).sort("occurred_at", -1).limit(50).to_list(50),
        
        "maintenance_history": [],  # Will populate in CMMS module
        
        "downtime_events": [],  # Will track
        
        "activity": await activity_service.get_entity_activity("asset", asset_id, 100)
    }
    
    return history

@router.post("/{asset_id}/qr-code")
async def generate_asset_qr_code(
    asset_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Generate QR code for asset"""
    import qrcode
    import base64
    
    asset = await db.assets.find_one({"id": asset_id})
    if not asset:
        raise HTTPException(404, "Asset not found")
    
    # Generate QR code with asset URL
    qr_data = f"https://app.example.com/assets/{asset_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        "qr_code": f"data:image/png;base64,{img_str}",
        "asset_tag": asset["asset_tag"],
        "url": qr_data
    }
```

**Frontend Pages:**

**Main Page: `/frontend/src/components/AssetsPage.tsx`**
```typescript
const AssetsPage = () => {
  const [assets, setAssets] = useState([]);
  const [filters, setFilters] = useState({
    asset_type: 'all',
    unit_id: 'all',
    status: 'all',
    search: ''
  });
  const [view, setView] = useState('grid'); // 'grid', 'list', 'map'
  
  const loadAssets = async () => {
    const params = new URLSearchParams();
    if (filters.asset_type !== 'all') params.append('asset_type', filters.asset_type);
    if (filters.unit_id !== 'all') params.append('unit_id', filters.unit_id);
    if (filters.status !== 'all') params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);
    
    const response = await axios.get(`/api/assets?${params}`);
    setAssets(response.data);
  };

  return (
    <ModernPageWrapper
      title="Asset Register"
      subtitle="Manage equipment, infrastructure, and resources"
      actions={
        <PermissionGuard permission="asset.create.organization">
          <Button onClick={() => navigate('/assets/new')}>
            <Plus className="h-4 w-4 mr-2" />
            Add Asset
          </Button>
        </PermissionGuard>
      }
    >
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total Assets</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{assets.length}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Operational</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {assets.filter(a => a.status === 'operational').length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">In Maintenance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {assets.filter(a => a.status === 'maintenance').length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Down</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {assets.filter(a => a.status === 'down').length}
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Critical (A-rated)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {assets.filter(a => a.criticality === 'A').length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-5 gap-4">
            <Select value={filters.asset_type} onValueChange={v => setFilters({...filters, asset_type: v})}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="equipment">Equipment</SelectItem>
                <SelectItem value="infrastructure">Infrastructure</SelectItem>
                <SelectItem value="vehicle">Vehicles</SelectItem>
                <SelectItem value="it_asset">IT Assets</SelectItem>
                <SelectItem value="safety_equipment">Safety Equipment</SelectItem>
                <SelectItem value="tool">Tools</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filters.status} onValueChange={v => setFilters({...filters, status: v})}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="operational">Operational</SelectItem>
                <SelectItem value="maintenance">Maintenance</SelectItem>
                <SelectItem value="down">Down</SelectItem>
                <SelectItem value="retired">Retired</SelectItem>
              </SelectContent>
            </Select>
            
            <Input
              placeholder="Search assets..."
              value={filters.search}
              onChange={e => setFilters({...filters, search: e.target.value})}
            />
            
            <div className="flex gap-2">
              <Button variant={view === 'grid' ? 'default' : 'outline'} onClick={() => setView('grid')}>
                <Grid className="h-4 w-4" />
              </Button>
              <Button variant={view === 'list' ? 'default' : 'outline'} onClick={() => setView('list')}>
                <List className="h-4 w-4" />
              </Button>
            </div>
            
            <Button onClick={() => exportAssets()}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Asset Grid/List */}
      {view === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {assets.map(asset => (
            <Card key={asset.id} className="cursor-pointer hover:shadow-lg" onClick={() => navigate(`/assets/${asset.id}`)}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-base">{asset.name}</CardTitle>
                    <CardDescription className="text-xs">
                      {asset.asset_tag}
                    </CardDescription>
                  </div>
                  <Badge variant={
                    asset.status === 'operational' ? 'default' :
                    asset.status === 'down' ? 'destructive' :
                    'secondary'
                  }>
                    {asset.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium capitalize">{asset.asset_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Criticality:</span>
                    <Badge variant={
                      asset.criticality === 'A' ? 'destructive' :
                      asset.criticality === 'B' ? 'default' :
                      'secondary'
                    }>
                      {asset.criticality}
                    </Badge>
                  </div>
                  {asset.next_maintenance_date && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Next PM:</span>
                      <span className="text-xs">{formatDate(asset.next_maintenance_date)}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Asset Tag</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Unit</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Criticality</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assets.map(asset => (
                  <TableRow key={asset.id}>
                    <TableCell className="font-mono text-sm">{asset.asset_tag}</TableCell>
                    <TableCell className="font-medium">{asset.name}</TableCell>
                    <TableCell className="capitalize">{asset.asset_type}</TableCell>
                    <TableCell>{asset.unit_name || 'N/A'}</TableCell>
                    <TableCell>
                      <Badge variant={asset.status === 'operational' ? 'default' : 'secondary'}>
                        {asset.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={asset.criticality === 'A' ? 'destructive' : 'outline'}>
                        {asset.criticality}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button size="sm" variant="ghost" onClick={() => navigate(`/assets/${asset.id}`)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <PermissionGuard permission="asset.update.organization">
                          <Button size="sm" variant="ghost" onClick={() => navigate(`/assets/${asset.id}/edit`)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                        </PermissionGuard>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </ModernPageWrapper>
  );
};
```

**Asset Detail Page: `/frontend/src/components/AssetDetailPage.tsx`**
```typescript
const AssetDetailPage = () => {
  const { assetId } = useParams();
  const [asset, setAsset] = useState(null);
  const [activeTab, setActiveTab] = useState('details');

  return (
    <ModernPageWrapper
      title={asset?.name || 'Loading...'}
      subtitle={`Asset Tag: ${asset?.asset_tag}`}
      actions={
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => printQRCode()}>
            <QrCode className="h-4 w-4 mr-2" />
            Print QR Code
          </Button>
          <PermissionGuard permission="asset.update.organization">
            <Button onClick={() => navigate(`/assets/${assetId}/edit`)}>
              <Edit className="h-4 w-4 mr-2" />
              Edit Asset
            </Button>
          </PermissionGuard>
        </div>
      }
    >
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="details">Details</TabsTrigger>
          <TabsTrigger value="maintenance">Maintenance History</TabsTrigger>
          <TabsTrigger value="inspections">Inspections</TabsTrigger>
          <TabsTrigger value="incidents">Incidents</TabsTrigger>
          <TabsTrigger value="attachments">Documents</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          {/* Asset details form/view */}
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Asset Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Asset Tag</Label>
                  <p className="font-mono">{asset?.asset_tag}</p>
                </div>
                <div>
                  <Label>Name</Label>
                  <p>{asset?.name}</p>
                </div>
                <div>
                  <Label>Description</Label>
                  <p>{asset?.description || 'N/A'}</p>
                </div>
                <div>
                  <Label>Type / Category</Label>
                  <p className="capitalize">{asset?.asset_type} / {asset?.category || 'N/A'}</p>
                </div>
                <div>
                  <Label>Criticality</Label>
                  <Badge variant={asset?.criticality === 'A' ? 'destructive' : 'outline'}>
                    {asset?.criticality} - {
                      asset?.criticality === 'A' ? 'Critical' :
                      asset?.criticality === 'B' ? 'Important' :
                      'Standard'
                    }
                  </Badge>
                </div>
                <div>
                  <Label>Status</Label>
                  <Badge>{asset?.status}</Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Technical Specifications</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Make / Model</Label>
                  <p>{asset?.make} / {asset?.model}</p>
                </div>
                <div>
                  <Label>Serial Number</Label>
                  <p className="font-mono">{asset?.serial_number}</p>
                </div>
                <div>
                  <Label>Manufacturer</Label>
                  <p>{asset?.manufacturer}</p>
                </div>
                <div>
                  <Label>Year</Label>
                  <p>{asset?.year_manufactured}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Location</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Organizational Unit</Label>
                  <p>{asset?.unit_name}</p>
                </div>
                <div>
                  <Label>Location Details</Label>
                  <p>{asset?.location_details || 'N/A'}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Financial</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Purchase Date</Label>
                  <p>{formatDate(asset?.purchase_date)}</p>
                </div>
                <div>
                  <Label>Purchase Cost</Label>
                  <p>${asset?.purchase_cost?.toLocaleString()}</p>
                </div>
                <div>
                  <Label>Current Value</Label>
                  <p>${asset?.current_value?.toLocaleString()}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="maintenance">
          {/* Work order history - will implement in CMMS module */}
          <Card>
            <CardHeader>
              <CardTitle>Maintenance History</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Work orders and maintenance records will appear here</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="inspections">
          {/* Linked inspections */}
          <Card>
            <CardHeader>
              <CardTitle>Inspection History</CardTitle>
            </CardHeader>
            <CardContent>
              {/* List of inspections where asset_id = this asset */}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="incidents">
          {/* Linked incidents */}
          <Card>
            <CardHeader>
              <CardTitle>Incident History</CardTitle>
            </CardHeader>
            <CardContent>
              {/* List of incidents involving this asset */}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="attachments">
          <AttachmentManager entityType="asset" entityId={assetId} />
        </TabsContent>

        <TabsContent value="activity">
          <ActivityTimeline entityType="asset" entityId={assetId} />
        </TabsContent>
      </Tabs>
    </ModernPageWrapper>
  );
};
```

**Asset Creation Form: `/frontend/src/components/AssetCreatePage.tsx`**
- Multi-step wizard (Basic Info → Technical → Location → Financial → Review)
- Field validation
- QR code generation on save
- Photo upload for asset

**Database Indexes:**
```javascript
db.assets.createIndex({ organization_id: 1, is_active: 1 })
db.assets.createIndex({ asset_tag: 1 }, { unique: true })
db.assets.createIndex({ unit_id: 1 })
db.assets.createIndex({ asset_type: 1, status: 1 })
db.assets.createIndex({ criticality: 1 })
```

**Effort:** 8-10 days  
**Team:** 1 backend + 1 frontend  
**Dependencies:** Unified services

---

### **2.2 WORK ORDER / CMMS MODULE**

**Purpose:** Formal maintenance management system

**This is TOO LONG. Let me create as a separate comprehensive document...**

Actually, this plan will be MASSIVE (200+ pages if fully detailed). Let me create a structured master plan document with the right level of detail.
