<template>
  <div class="survey-component">
    <h3 class="survey-title">Please provide a name for the survey</h3>
    <input type="text" v-model="surveyName" class="survey-input" placeholder="Name" />
    <div>
      <h3 class="survey-title">Variants</h3>
      <div v-for="(option, index) in options" :key="`option-${index}`" class="survey-input-group">
        <OptionComponent
          :option="option"
          @update-option="updateOption(index, $event)"
          @remove-option="removeOption(index)"
        />
      </div>
      <button class="survey-button add-button" @click="addOption">+</button>
    </div>
    <div>
      <h3 class="survey-title">Criteria</h3>
      <div v-for="(criterion, index) in criteria" :key="`criterion-${index}`" class="survey-input-group">
        <CriterionComponent
          :criterion="criterion"
          @update-criterion="updateCriterion(index, $event)"
          @remove-criterion="removeCriterion(index)"
        />
      </div>
      <button class="survey-button add-button" @click="addCriterion">+</button>
    </div>
    <button class="survey-button save-button" @click="saveSurvey">Save survey</button>
  </div>
</template>

<script>
import axios from 'axios';
import OptionComponent from './OptionComponent.vue';
import CriterionComponent from './CriterionComponent.vue';

export default {
  name: 'SurveyComponent',
  components: {
    OptionComponent,
    CriterionComponent
  },
  data() {
    return {
      surveyName: '',
      options: [{ name: '', description: '' }],
      criteria: [{ name: '', description: '' }]
    };
  },
  methods: {
    addOption() {
      this.options.push({ name: '', description: '' });
    },
    removeOption(index) {
      this.options.splice(index, 1);
    },
    updateOption(index, updatedOption) {
      this.options.splice(index, 1, updatedOption);
    },
    addCriterion() {
      this.criteria.push({ name: '', description: '' });
    },
    removeCriterion(index) {
      this.criteria.splice(index, 1);
    },
    updateCriterion(index, updatedCriterion) {
      this.criteria.splice(index, 1, updatedCriterion);
    },

    async saveSurvey() {
      const surveyData = {
        name: this.surveyName,
        options: this.options,
        criteria: this.criteria
      };

      try {
        const response = await axios.post('/api/save-survey', surveyData);
        console.log('Server response:', response.data);
        alert('The survey was saved successfully!');
      } catch (error) {
        if (error.response) {
          console.error('Error saving survey:', error.response.data);
        } else if (error.request) {
          console.error('No response from server:', error.request);
        } else {
          console.error('Query configuration error:', error.message);
        }
        alert('An error occurred while saving the survey.');
      }
    }
  }
};
</script>

<style lang="scss">
@import './survey-styles.scss';
</style>
