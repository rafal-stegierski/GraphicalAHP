<template>
  <div class="comparison-slider">
    <table>
      <tr>
        <td colspan="3"><h2> Criterion {{ criterion }}</h2></td> 
      </tr>
      <tr>
        <td>
          <!-- Lewa lista rozwijana -->
          <select v-model="leftValue" @change="handleLeftChange">
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7">7</option>
            <option value="8">8</option>
            <option value="9">9</option>
          </select>
        </td>
        <td>
          <!-- Prawa lista rozwijana -->
          <select v-model="rightValue" @change="handleRightChange">
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7">7</option>
            <option value="8">8</option>
            <option value="9">9</option>
          </select>
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
export default {
  name: 'ClassicSliderComponent',
  props: {
    optionA: String,
    optionB: String,
    criterion: String,
    sliderIndex: Number,
  },
  data() {
    return {
      leftValue: '1',  
      rightValue: '1', 
    };
  },
  methods: {
    handleLeftChange() {
      if (this.leftValue !== '1') {
        this.rightValue = '1'; 
      }
      this.emitSelectedValue();
    },
    handleRightChange() {
      if (this.rightValue !== '1') {
        this.leftValue = '1'; 
      }
      this.emitSelectedValue();
    },
    emitSelectedValue() {
      let leftValueNumeric = parseFloat(this.leftValue);
      let rightValueNumeric = parseFloat(this.rightValue);

      if (this.leftValue !== '1') {
        rightValueNumeric = 1 / leftValueNumeric;
      }
      else if (this.rightValue !== '1') {
        leftValueNumeric = 1 / rightValueNumeric;
      }
      console.log(`Emitting values for slider ${this.sliderIndex}: left = ${leftValueNumeric}, right = ${rightValueNumeric}`);
      this.$emit('sliderValueChanged', this.sliderIndex, { leftValue: leftValueNumeric, rightValue: rightValueNumeric });
    }
  },
  mounted() {
    this.emitSelectedValue();  
    console.log(`ClassicSliderComponent loaded for criterion: ${this.criterion} with options: ${this.optionA} vs ${this.optionB}`);
  }
};
</script>

<style scoped>
select {
  width: 150px; 
  padding: 10px; 
  font-size: 18px; 
  margin: 0 20px; 
}

td {
  width: 50%;
  text-align: center;
}
</style>
