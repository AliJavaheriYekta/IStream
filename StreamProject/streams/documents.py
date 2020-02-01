from .models import Stream
from accounts.models import User
from elasticsearch_dsl import analyzer, analysis, tokenizer
from django_elasticsearch_dsl import DocType, Index, fields
from taggit.managers import TaggableManager, TaggedItem


mstream = Index('streams')
mstream.settings(
    number_of_shards=1,
    number_of_replicas=0
)

autocomplete_filter = analysis.token_filter("autocomplete_filter", type="edge_ngram", min_gram=1, max_gram=20)

autocomplete = analyzer(
    'autocomplete',
    tokenizer="standard",
    filter=["standard", "lowercase", "snowball", autocomplete_filter]
)

mstream.analyzer(autocomplete)

@mstream.doc_type
class StreamIndex(DocType):

    id = fields.IntegerField()
    user_name = fields.TextField(analyzer=autocomplete)
    game = fields.TextField(analyzer=autocomplete)

    class Meta:
        model = Stream
        analyzer = autocomplete
   
    def url(self):
        return Stream.objects.get(pk=self.id).get_absolute_url()
