<template>
  <div class="survey-list">
    <h1>Survey List</h1>
    <button @click="fetchSurveys" class="refresh-button">Refresh survey list</button>
    <div v-if="surveys.length > 0">
      <div v-for="survey in surveys" :key="survey.id" class="survey-item">
        <div class="survey-header">
          <div style="clear: both">
          <h3>{{ survey.name }}</h3>
          <p>Number of survey completions: {{ survey.submissionsCount }}</p>
          </div>
          <div class="actions">
            <button @click="viewDetails(survey)">Show details</button>
            <button @click="viewSubmissions(survey)">Survey completion</button>
            <button v-if="role === 'admin'" @click="deleteSurvey(survey.id)">Delete</button>
            <button @click="downloadFile(survey.id)">Download</button>
            <button @click="calculateAHP(survey.id, 'classic')">Calculate Classic AHP</button>
            <button @click="calculateAHP(survey.id, 'drawing')">Calculate Drawing AHP</button>
          </div>
        </div>

        <div v-if="selectedSurvey && selectedSurvey.id === survey.id && showDetails" class="survey-details">
          <h4>Survey details: {{ survey.name }}</h4>
          <div class="survey-options">
            <div><strong>Variants:</strong> {{ survey.options.map(o => o.name).join(', ') }}</div>
            <div><strong>Criteria:</strong> {{ survey.criteria.map(c => c.name).join(', ') }}</div>
          </div>
          <button @click="hideDetails">Close details</button>
        </div>

        <div v-if="selectedSurvey && selectedSurvey.id === survey.id && showSubmissions" class="survey-submissions">
          <div v-if="showModalView" class="modal-overlay">
          <div class="modal-content">

          <h4>All survey completions:{{ survey.name }}</h4>
          <div v-for="(submission, index) in survey.submissions" :key="index" class="submission-item">
            <p><strong>Submission {{ index + 1 }}:</strong>
            <table class="survey-table">
            <tr><th>Expert Name</th><th>Option A</th><th>Option B</th><th>Survey Type</th><th v-if=" submission.survey_type === 'classic'">Left Value</th><th v-if=" submission.survey_type === 'drawing'">Drawing</th></tr>
            <tr><td>{{ submission.expertName }}</td><td></td><td></td><td>{{ submission.survey_type }}</td><td></td></tr>
            <tr v-for="(result, index) in submission.results" :key="index"><td></td><td>{{ result.optionA }}</td><td>{{ result.optionB }}</td><td></td><td v-if="result.value.leftValue">{{ result.value.leftValue.toFixed(2) }}</td>
            <td v-if="submission.survey_type === 'drawing'">
            <div v-html="svg(result.value)"></div>
            </td></tr>
            </table>
            </p>
<!--        <button @click="viewSubmissionDetails(submission)">Details</button>  -->
            <button v-if="role === 'admin'"  @click="deleteSubmission(submission.id)">Delete</button>
          </div>
          <button @click="hideSubmissions">Close survey completions</button>
          </div>
          </div>
        </div>
      </div>
    </div>
    <p v-else>No surveys available.</p>

    <div v-if="showModal" class="modal-overlay">
  <div class="modal-content">
    <h2>AHP Results</h2>
    
    <p><strong>Average Preference Vector</strong></p>

    <table v-if="ahpResults?.average_preference_vector" class="survey-table-narrow">
    <tr v-for="(value, index) in ahpResults.average_preference_vector" :key="index">
      <td class="td-header">{{ ahpResults.options[index] }}</td><td>{{ value.toFixed(2) }}</td>
    </tr>
    </table>

    <p><strong>All Preference Vectors</strong></p>

    <table  v-if="ahpResults?.all_preference_vectors" class="survey-table">
    <tr> 
      <td v-for="(value, index) in ahpResults.options" :key="index">
        {{ value }}
      </td>
    </tr>
    
    <tr v-for="(vector, index) in ahpResults.all_preference_vectors" :key="index">
      <td v-for="(element, indx) in vector" :key="indx">{{ element.toFixed(2) }}</td>
    </tr>
    </table>

    <p><strong>Average Consistency Ratio</strong><br><br> {{ ahpResults?.average_cr.toFixed(2) || 'No data' }}</p>
    
    <p><strong>All Consistency Ratios</strong></p>
    <div v-if="ahpResults?.all_cr_values" style="clear: both">
      <div v-for="(cr, index) in ahpResults.all_cr_values" :key="index" class="cr">
        {{ cr.toFixed(2) }}
      </div>
    </div>
    <div style="clear: both">
    <button @click="closeModal">Close</button>
    </div>
  </div>
</div>

</div>
</template>

<script>
import axios from 'axios';
import { saveAs } from 'file-saver';


export default {
  computed: {
    ruseRole() {
      return localStorage.getItem("userrole");
    },
  },
  data() {
    return {
      surveys: [],
      selectedSurvey: null,
      showDetails: false,
      showSubmissions: false,
      ahpResults: null,
      showModal: false,
      showModalView: false
    };
  },
  methods: {
    svg(data) {
      const points = data.map(({ x, y }) => [x, y]).flat();
      const first_x = points[0];
      const last_x = points[points.length-2];
      const range_x = last_x - first_x;
      const scale_x = 200./range_x;
      let min_y = points[1];
      let max_y = min_y;
      for(let i=0; i<points.length/2; i++) {
        points[i*2] -= first_x;
        points[i*2] *= scale_x;
        if(min_y > points[i*2+1]) {
          min_y = points[i*2+1];
        }
        if(max_y < points[i*2+1]) {
          max_y = points[i*2+1];
        }
      }
      const scale_y = 100./(max_y-min_y);
      for(let i=0; i<points.length/2; i++) {
        points[i*2+1] -= min_y;
        points[i*2+1] *= scale_y;
      }
      return `<svg width="200" height="100">
            <rect width="100%" height="100%" fill="white" />
            <polyline points="${points.join(', ')}" fill="none" stroke="black" stroke-width="1" />
            </svg>`;
    },
    async fetchSurveys() {
  try {
    const response = await axios.get('/api/surveys');
    console.log("Surveys data:", response.data);
    this.surveys = response.data;

    for (let survey of this.surveys) {
      const countResponse = await axios.get(`/api/survey-results/count/${survey.id}`);
      console.log(`Count for survey ${survey.id}:`, countResponse.data.count);
      survey.submissionsCount = countResponse.data.count;

      const submissionsResponse = await axios.get(`/api/survey-results/${survey.id}`);
      console.log(`Submissions for survey ${survey.id}:`, submissionsResponse.data);
      survey.submissions = submissionsResponse.data;
    }
  } catch (error) {
    console.error('Błąd podczas pobierania ankiet:', error);
  }
},
closeModal() {
    this.showModal = false;
  },
async calculateAHP(surveyId, method) {
  try {
    const survey = this.surveys.find(s => s.id === surveyId);
    
    if (!survey || !survey.submissions || survey.submissions.length === 0) {
      alert('Brak uzupełnień dla tej ankiety. Nie można obliczyć wyników AHP.');
      return;
    }
  
      const response = await axios.get(`/api/survey-results/${surveyId}/calculate`, {
          params: { method: method }
      });
      console.log("Dane otrzymane z backendu:", response.data);
      this.ahpResults = response.data;
      this.showModal = true;
  } catch (error) {
      console.error(`Błąd podczas obliczania AHP (${method}) dla ankiety ${surveyId}:`, error);
  }
}
,
    viewDetails(survey) {
      this.selectedSurvey = survey;
      this.showDetails = true;
      this.showSubmissions = false;
    },
    hideDetails() {
      this.showDetails = false;
    },
    viewSubmissions(survey) {
      this.selectedSurvey = survey;
      this.showDetails = false;
      this.showSubmissions = true;
      this.showModalView = true;
    },
    hideSubmissions() {
      this.showSubmissions = false;
    },
    async deleteSurvey(surveyId) {
      if (confirm('Czy na pewno chcesz usunąć tę ankietę?')) {
        try {
          await axios.delete(`/api/surveys/${surveyId}`);
          this.fetchSurveys();
        } catch (error) {
          console.error('Błąd podczas usuwania ankiety:', error);
        }
      }
    },
    async downloadFile(surveyId) {
        try {
            const response = await axios.get(`/api/survey-results/${surveyId}/download`, { responseType: 'arraybuffer' });
            const blob = new Blob([response.data], { type: 'application/octet-stream' });
            saveAs(blob, `${surveyId}.xlsx`);
        } catch (error) {
            console.error('Can\' download data');
        }
    },
    async viewSubmissionDetails(submission) {
      alert(`Szczegóły uzupełnienia: ${JSON.stringify(submission)}`);
    },
    async deleteSubmission(submissionId) {
      if (confirm('Czy na pewno chcesz usunąć to uzupełnienie?')) {
        try {
          await axios.delete(`/api/survey-results/${submissionId}`);
          this.fetchSurveySubmissions(this.selectedSurvey.id);
        } catch (error) {
          console.error('Błąd podczas usuwania uzupełnienia:', error);
        }
      }
    },
    formatSubmission(submission) {
      let table = '<table><tr><th>Expert Name</th><th>Option A</th><th>Option B</th></tr>';
      table += '<tr><td>' + submission.expertName + '</td></tr></table>';
      return table;
    }
  },
  mounted() {
    this.fetchSurveys();
  }
};
</script>

<style scoped>
.survey-list {
  text-align: center;
}

.refresh-button {
  margin-bottom: 20px;
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.survey-item {
  border: 1px solid #ddd;
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 5px;
  background-color: #f9f9f9;
  position: relative;
}

.survey-header {
  justify-content: space-between;
  align-items: center;
}

.actions {
  clear: both;
  gap: 10px;
}

.survey-details {
  margin-top: 15px;
  padding: 10px;
  background-color: #e9f7ff;
  border-radius: 5px;
  border: 1px solid #007bff;
}

.survey-submissions {
  margin: 0px;
  padding: 0px;
}

.survey-options {
  justify-content: space-between;
}

.submission-item {
  border-bottom: 1px solid #ccc;
  padding: 10px 0;
  margin-bottom: 10px;
}

.submission-item:last-child {
  border-bottom: none;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 80vw;
  height: 80vh;
  max-width: 90%;
  text-align: center;
  position: relative;
  overflow: scroll;
}

.survey-table {
  margin: auto;
  width: 90%;
  border: solid 0px;
  border-collapse: collapse;
  table-layout: fixed;
}

.survey-table-narrow {
  margin: auto;
  width: 40%;
  border: solid 0px;
  border-collapse: collapse;
  table-layout: fixed;
}

.survey td {
  border: solid 0px;
}

.td-header {
  font-weight: bold;
  text-align: left;
}

.survey-table tr:nth-child(even) {
  background-color: #ffffff;
}

.survey-table tr:nth-child(odd) {
  background-color: #eeeeee;
}

.survey-table-narrow tr:nth-child(even) {
  background-color: #ffffff;
}

.survey-table-narrow tr:nth-child(odd) {
  background-color: #eeeeee;
}


.survey-table tr:first-child {
  background-color: #dddddd;
  font-weight: bold;
}

.cr {
    margin-left: 1em;
    margin-right: 1em;
    width: 5em;
    text-align: center;
    float: left;
}

button {
  margin-top: 20px;
}
</style>
