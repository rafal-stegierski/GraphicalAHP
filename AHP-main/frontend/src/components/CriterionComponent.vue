<template>
  <div class="survey-input-group">
    <input
      type="text"
      :value="criterion.name"
      @input="$emit('update-criterion', { ...criterion, name: $event.target.value })"
      placeholder="Critetion Name "
      class="survey-input"
    />
    <textarea
      :value="criterion.description"
      @input="$emit('update-criterion', { ...criterion, description: $event.target.value })"
      placeholder="Critetion Description"
      class="survey-textarea"
    ></textarea>
    <button @click="$emit('remove-criterion')" class="survey-button remove-button">-</button>
  </div>
</template>

<script>
export default {
  props: ['criterion'],
  emits: ['update-criterion', 'remove-criterion']
};
</script>

<style lang="scss">
@import './survey-styles.scss';
</style>
