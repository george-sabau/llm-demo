import de.hybris.platform.core.model.media.MediaModel
import de.hybris.platform.servicelayer.media.MediaService
import de.hybris.platform.servicelayer.model.ModelService
import de.hybris.platform.servicelayer.search.FlexibleSearchQuery

import java.nio.charset.StandardCharsets

// ----------------------------
// CONFIGURATION
// ----------------------------
def mediaCode = "saparticle_export"
def fileName = "saparticle_export.csv"

// ----------------------------
// FLEXIBLESEARCH QUERY
// ----------------------------
def fsQuery = """
    SELECT {a:pk} 
    FROM {SapArticle AS a
          JOIN BaseProduct AS b ON {a.baseProduct} = {b.pk}}
    WHERE {a.baseProduct} IS NOT NULL
"""

def query = new FlexibleSearchQuery(fsQuery)
def results = flexibleSearchService.search(query)

def filtered = results.getResult().findAll { it.order == 0 } // or map correctly
// ----------------------------
// CREATE CSV CONTENT
// ----------------------------
def csv = new StringBuilder()
csv << "articleCode,baseProductCode\n"
filtered.each { a ->
    csv << "${a.code},${a.baseProduct.code}\n"
}

// ----------------------------
// STORE CSV AS MEDIA
// ----------------------------
def mediaService = spring.getBean("mediaService", MediaService)
def modelService = spring.getBean("modelService", ModelService)

MediaModel media = mediaService.getMedia("domainCorpus")

// Store CSV bytes in Media
def bytes = csv.toString().getBytes(StandardCharsets.UTF_8)
mediaService.setDataForMedia(media, bytes)
modelService.save(media)

println "CSV successfully stored in media with code 'domainCorpus'!"
println "Download it from HAC or backoffice via media download URL."
