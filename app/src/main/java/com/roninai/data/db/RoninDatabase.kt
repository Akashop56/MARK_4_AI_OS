package com.roninai.data.db

import android.content.Context
import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.Room
import androidx.room.RoomDatabase
import kotlinx.coroutines.flow.Flow

@Entity(tableName = "long_term_memories")
data class LongTermMemoryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val content: String,
    val reason: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "experiences")
data class ExperienceEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val problem: String,
    val analysis: String,
    val solution: String,
    val futureImprovement: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Dao
interface LongTermMemoryDao {
    @Query("SELECT * FROM long_term_memories ORDER BY createdAt DESC")
    fun observeAll(): Flow<List<LongTermMemoryEntity>>

    @Insert
    suspend fun insert(memory: LongTermMemoryEntity)
}

@Dao
interface ExperienceDao {
    @Query("SELECT * FROM experiences ORDER BY createdAt DESC")
    fun observeAll(): Flow<List<ExperienceEntity>>

    @Insert
    suspend fun insert(experience: ExperienceEntity)
}

@Database(entities = [LongTermMemoryEntity::class, ExperienceEntity::class], version = 1)
abstract class RoninDatabase : RoomDatabase() {
    abstract fun longTermMemoryDao(): LongTermMemoryDao
    abstract fun experienceDao(): ExperienceDao

    companion object {
        fun create(context: Context): RoninDatabase = Room.databaseBuilder(
            context.applicationContext,
            RoninDatabase::class.java,
            "ronin_brain.db"
        ).fallbackToDestructiveMigration().build()
    }
}
