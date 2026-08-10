package com.roninai.experience

import com.roninai.data.db.ExperienceDao
import com.roninai.data.db.ExperienceEntity
import kotlinx.coroutines.flow.Flow

class ExperienceSystem(private val dao: ExperienceDao) {
    fun observe(): Flow<List<ExperienceEntity>> = dao.observeAll()

    suspend fun record(problem: String, analysis: String, solution: String, futureImprovement: String) {
        dao.insert(ExperienceEntity(problem = problem, analysis = analysis, solution = solution, futureImprovement = futureImprovement))
    }
}
