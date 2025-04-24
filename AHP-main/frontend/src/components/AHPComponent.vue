<template>
  <div class="ahp-container">
    <!--<h1>AHP Analysis</h1> -->

    <!-- Single comparison -->
    <div v-if="currentComparison !== null" class="comparison-container">
      <!-- Wyświetlanie aktualnego kryterium wyżej -->
      <!--<h2 v-if="pairs[currentComparison]" class="criterion-title">{{ pairs[currentComparison].criterion }}</h2> -->

      <!-- Left option -->
      <div class="option-left option-tile">{{ pairs[currentComparison].optionA }}</div>

      <!-- Drawing area -->
      <div class="drawing-area">
        <component
          :is="getSliderComponent(pairs[currentComparison])"
          :key="'pair-' + pairs[currentComparison].id"
          :optionA="pairs[currentComparison].optionA"
          :optionB="pairs[currentComparison].optionB"
          :criterion="pairs[currentComparison].criterion"
          :sliderIndex="pairs[currentComparison].id"
          @sliderValueChanged="updateSliderValue"
          @drawingCompleted="handleDrawingCompleted"
          @drawingStatusChanged="handleDrawingStatusChanged"
        />
      </div>

      <!-- Right option -->
      <div class="option-right option-tile">{{ pairs[currentComparison].optionB }}</div>
    </div>

    <!-- Next and submit buttons -->
    <div class="button-container">
      <button 
        class="next-btn" 
        :disabled="sliderType === 'drawing' && !hasDrawnSomething" 
        @click="nextComparison" 
        v-if="currentComparison < pairs.length - 1"
      >
        Next
      </button>

      <button 
        class="next-btn"
        :disabled="sliderType === 'drawing' && !hasDrawnSomething"
        @click="submitData"
        v-if="currentComparison === pairs.length - 1"
      >
        {{ sliderType === 'drawing' ? 'Send data' : 'Save and send data' }}
      </button>
    </div>
  </div>
</template>

<script>

import DrawingSliderComponent from './DrawingSliderComponent.vue';
import ClassicSliderComponent from './ClassicSliderComponent.vue';

export default {
  components: {

    DrawingSliderComponent,
    ClassicSliderComponent
  },
  props: {
    sliderType: {
      type: String,
      required: true
    },
    options: {
      type: Array,
      required: true
    },
    criteria: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      pairs: [],
      currentComparison: 0,
      hasDrawnSomething: false
    };
  },
  created() {
    this.generatePairs();
  },
  methods: {
    handleDrawingStatusChanged(status) {
      if (this.sliderType === 'drawing') {
        this.hasDrawnSomething = status;
      }
    },
    getSliderComponent() {
      if (this.sliderType === 'classic') return 'ClassicSliderComponent';
      if (this.sliderType === 'drawing') return 'DrawingSliderComponent';
      return null;
    },
    nextComparison() {
      if (this.currentComparison < this.pairs.length - 1) {
        this.currentComparison++;
        if (this.sliderType === 'drawing') {
          this.hasDrawnSomething = false;
        }
      }
    },
    generatePairs() {
      this.pairs = [];
      let id = 1;
      this.criteria.forEach((criterion) => {
        this.options.forEach((optionA, indexA) => {
          this.options.forEach((optionB, indexB) => {
            if (indexA < indexB) {
              const newPair = {
                id: id++,
                optionA: optionA.name,
                optionB: optionB.name,
                criterion: criterion.name
              };
              this.pairs.push(newPair);
            }
          });
        });
      });
    },
    updateSliderValue(id, value) {
      const pair = this.pairs.find(pair => pair.id === id);
      if (pair) {
        pair.sliderValue = value;
      } else {
        console.error(`Cant't find slider with ID: ${id}`);
      }
    },
    submitData() {
  const dataToSubmit = {
    type: this.sliderType,
    comparisons: this.pairs.map((pair) => {
      const value = pair.sliderValue || { leftValue: 1, rightValue: 1 };
      console.log(`Submitting comparison for ${pair.optionA} vs ${pair.optionB}:`, value);
      return {
        id: pair.id,
        criterion: pair.criterion,
        optionA: pair.optionA,
        optionB: pair.optionB,
        value: value
      };
    })
  };
  console.log('Final data to submit:', dataToSubmit);
  this.$emit('save-data', dataToSubmit);
},
    handleDrawingCompleted(payload) {
      const pair = this.pairs.find(pair => pair.id === payload.sliderIndex);
      if (pair) {
        pair.sliderValue = payload.drawingData;
      } else {
        console.warn(`Can't find slider with ID: ${payload.sliderIndex}`);
      }
    }
  }
};
</script>

<style scoped>
.ahp-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  width: 1000px;
  height: 80vh;
  text-align: center;
  box-sizing: border-box;
}

.comparison-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 90vw;
  margin-bottom: 20px;
}

.option-left, .option-right {
  width: 10%; 
  padding: 20px;
  background-color: #e0f7fa;
  border-radius: 15px;
  font-size: 24px;
  font-weight: bold;
  text-align: center;
}

.drawing-area {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 80%;
  height: 60vh;
  max-width: 1200px;
  box-sizing: border-box;
}

.button-container {
  margin-top: 20px;
  width: 100%;
  display: flex;
  justify-content: center;
}

.next-btn {
  width: 100%;
  background-color: navy;
  color: white;
  font-size: 24px;
  padding: 15px;
  border-radius: 10px;
  border: 1px solid black;
  cursor: pointer;
}

.next-btn:disabled {
  background-color: lightgray;
  cursor: not-allowed;
}

.criterion-title {
  position: absolute;
  top: 10px;
  width: 100%;
  text-align: center;
  font-size: 24px;
  font-weight: bold;
}
</style>
