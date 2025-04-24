<template>
  <div class="survey-input-group">
    <input
      type="text"
      :value="option.name"
      @input="$emit('update-option', { ...option, name: $event.target.value })"
      placeholder="Variant Name"
      class="survey-input"
    />
    <textarea
      :value="option.description"
      @input="$emit('update-option', { ...option, description: $event.target.value })"
      placeholder="Variant Description"
      class="survey-textarea"
    ></textarea>
    <button @click="$emit('remove-option')" class="survey-button remove-button">-</button>
  </div>
</template>

<script>
export default {
  props: ['option'],
  emits: ['update-option', 'remove-option']
};
</script>

<style lang="scss">
@import './survey-styles.scss';
</style>
