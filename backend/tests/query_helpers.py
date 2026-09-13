"""試験の準備とDB状態確認に使用する型とqueryを明示する。"""

from kotorelay.generated.models import ChunksRow as ChunksRow
from kotorelay.generated.models import OrganizationsRow as OrganizationsRow
from kotorelay.operations.chat.ask_question.generated.queries import (
    documents_list as documents_list,
)
from kotorelay.operations.chat.shared.generated.queries import documents_get as documents_get
from kotorelay.operations.chat.shared.generated.queries import ocr_runs_get as ocr_runs_get
from kotorelay.operations.documents.list_documents.generated.queries import (
    submissions_list as submissions_list,
)
from kotorelay.operations.indexing.shared.generated.queries import chunks_insert as chunks_insert
from kotorelay.operations.system.authorization.generated.queries import (
    organizations_fence as organizations_fence,
)
from kotorelay.operations.system.authorization.generated.queries import (
    organizations_get as organizations_get,
)
