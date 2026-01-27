import de.hybris.platform.servicelayer.search.FlexibleSearchQuery
import de.hybris.platform.core.model.media.MediaModel
import de.hybris.platform.servicelayer.media.MediaService
import de.hybris.platform.servicelayer.model.ModelService

// ----------------------------
// FLEXIBLESEARCH QUERY
// ----------------------------
def fsQuery = """
    SELECT 
        {a:pk}
    FROM {SapArticle AS a
          JOIN BaseProduct AS b ON {a:baseProduct} = {b:pk}}
    WHERE {a:baseProduct} IS NOT NULL
"""

def query = new FlexibleSearchQuery(fsQuery)
def results = flexibleSearchService.search(query).getResult()

// ----------------------------
// GROUP BY BASE PRODUCT
// ----------------------------
def grouped = results.groupBy { it.baseProduct }
def selected = []

grouped.each { baseCode, articles ->
    // Pick order='0' first if exists, otherwise first
    def chosen = articles.find { it.order == '0' } ?: articles[0]
    selected << chosen
}

// ----------------------------
// CREATE CSV
// ----------------------------
def csv = new StringBuilder()
selected.each { row ->
    csv << "${row.code},${row.baseProduct.code}\n"
}

// ----------------------------
// STORE CSV AS MEDIA
// ----------------------------
def mediaService = spring.getBean("mediaService", MediaService)
def modelService = spring.getBean("modelService", ModelService)

MediaModel media = mediaService.getMedia("domainCorpus") // replace with your media code

def bytes = csv.toString().getBytes("UTF-8")
mediaService.setDataForMedia(media, bytes)
modelService.save(media)

println "CSV successfully stored in media 'domainCorpus'"
