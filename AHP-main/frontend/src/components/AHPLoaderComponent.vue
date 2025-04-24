<template>
  <div class="ahp-container">
    <div v-if="!showAHP" class="config-container">
      <h3>Enter the name of the expert</h3>
      <input type="text" v-model="expertName" placeholder="Name of the expert" />
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <h3>Choose survey to complete</h3>
      <select v-if="surveys.length > 0" v-model="selectedSurvey" @change="loadSurvey">
        <option v-for="survey in surveys" :key="survey.id" :value="survey">
          {{ survey.name }}
        </option>
      </select>

      <h3 v-if="dataLoaded">Choose a survey type</h3>
      <select v-if="dataLoaded" v-model="sliderType">
        
        <option value="drawing">AHP drawing method</option>
        <option value="classic">Classic method</option>
      </select>

      <button v-if="dataLoaded" @click="initiateAHP">Initiate AHP</button>
    </div>

    <div class="ahp-component-wrapper" v-if="showAHP">
      <AHPComponent
        v-if="showAHP"
        :sliderType="sliderType"
        :options="options"
        :criteria="criteria"
        @save-data="handleSaveData"
      ></AHPComponent>
    </div>

    <SurveyCheck
      v-if="showSurvey"
      :options="options"
      :criteria="criteria"
    ></SurveyCheck>

    <p v-if="saveStatus === 'success'" style="color: green;">Survey results saved successfully!</p>
    <p v-if="saveStatus === 'error'" style="color: red;">Error saving survey results.</p>
  </div>

  <div>
    <p v-if="!finalResults">No results to display. Complete the survey to see the results.</p>
    <div v-if="finalResults">
      <h3>Survey results</h3>
      <ul>
        <li v-for="(result, index) in finalResults" :key="index">
          <strong>{{ result.option }}:</strong> {{ result.preference }}
        </li>
      </ul>
      <p><strong>Consistency Ratio (CR):</strong> {{ consistencyRatio }}</p>
    </div>
  </div>
</template>

<script>
import AHPComponent from './AHPComponent.vue';
import SurveyCheck from './SurveyCheck.vue';
import axios from 'axios';

export default {
  name: 'AHPLoaderComponent',
  components: {
    AHPComponent,
    SurveyCheck,
  },
  data() {
    return {
      surveys: [],
      selectedSurvey: null,
      options: [],
      criteria: [],
      expertName: '',
      sliderType: 'classic',
      dataLoaded: false,
      showAHP: false,
      showSurvey: false,
      saveStatus: '',
      finalResults: null,
      consistencyRatio: null,
      collectedResults: null,
      errorMessage: '',
    };
  },
  mounted() {
    this.fetchSurveys();
  },
  methods: {
    async fetchSurveys() {
      try {
        const response = await axios.get('/api/surveys');
        this.surveys = response.data;
      } catch (error) {
        console.error('Surveys downloading errors:', error);
      }
    },
    loadSurvey() {
      if (this.selectedSurvey) {
        this.options = this.selectedSurvey.options;
        this.criteria = this.selectedSurvey.criteria;
        this.dataLoaded = true;
      }
    },
    initiateAHP() {
      if (!this.expertName) {
        this.errorMessage = 'Please provide the name of the expert.';
        return;
      }
      this.errorMessage = '';
      this.showAHP = true;
      this.showSurvey = false;
    },
    handleSaveData(data) {
      if (data && data.comparisons) {
        this.collectedResults = { ...data, type: this.sliderType };
        console.log('Data from AHPComponent:', this.collectedResults);
        this.saveSurveyResults();
      } else {
        console.error('No data from AHPComponent');
      }
    },
    async calculateResults() {
      try {
        const response = await axios.post(`/api/survey-results/calculate`, {
          survey_id: this.selectedSurvey.id,
          method: this.sliderType,
          comparisons: this.collectedResults.comparisons,
        });

        if (response.data.final_preference_vector.length !== this.options.length) {
          console.error('Number of options is different to preference vector length');
          return;
        }

        this.finalResults = this.options.map((option, index) => ({
          option: option.name,
          preference: response.data.final_preference_vector[index],
        }));

        this.consistencyRatio = response.data.consistency_ratio;
      } catch (error) {
        console.error('Error of survey calculation:', error);
      }
    },
    async saveSurveyResults() {
      if (!this.collectedResults || !this.collectedResults.comparisons) {
        console.error('Error: No collected results to save');
        return;
      }

      const surveyResults = {
        survey_id: this.selectedSurvey.id,
        expertName: this.expertName,
        survey_type: this.sliderType,
        results: this.collectedResults.comparisons,
      };

      try {
        const response = await axios.post('/api/save-survey-results', surveyResults);
        console.log('Results saved correctly! ', response.data);
        this.saveStatus = 'success';
        alert(`Results saved correctly! ID: ${response.data.submission_id}`);
        await this.calculateResults();
        this.$router.push('/');
      } catch (error) {
        console.error('Error saving survey results:', error);
        this.saveStatus = 'error';
      }
    },
  },
};
</script>

<style scoped>
.ahp-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 100%;
  max-width: 1500px;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  margin-left: auto;
  margin-right: auto;
}
.ahp-component-wrapper {
  width: 100%;
  height: 80vh;
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
}
input, select, button {
  margin-bottom: 15px;
  padding: 10px;
  font-size: 16px;
  width: 200px;
  text-align: center;
}
.config-container {
  border: 2px solid #ccc;
  padding: 20px;
  margin-bottom: 20px;
}
.error-message {
  color: red;
  font-weight: bold;
}
button {
  width: 220px;
}
</style>
