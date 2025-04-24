<template>
  <div class="survey-check-container">
    <h1>Survey Check</h1>

   <!-- Lista otrzymanych opcji -->
<!-- Lista otrzymanych opcji -->
<div>
  <h2>Received Options:</h2>
  <ul>
    <li v-for="(option, index) in options" :key="'option-' + index">
      Name: {{ option.name }}, Description: {{ option.description || 'None' }}
    </li>
  </ul>
</div>

<!-- Lista otrzymanych kryteriów -->
<div>
  <h2>Received Criteria:</h2>
  <ul>
    <li v-for="(criterion, index) in criteria" :key="'criterion-' + index">
      Name: {{ criterion.name }}, Description: {{ criterion.description || 'None' }}
    </li>
  </ul>
</div>

</div>

</template>

<script>
export default {
  props: {
    options: {
      type: Array,
      default: () => []
    },
    criteria: {
      type: Array,
      default: () => []
    }
  }
};
</script>
