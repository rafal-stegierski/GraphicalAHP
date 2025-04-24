<template>
  <div class="comparison-slider">
    <table>
      <tr>
        <!-- <td colspan="3"><h2>{{ criterion }}</h2></td> -->
		<td colspan="3"><h2> Criterion {{ criterion }}</h2></td> 
      </tr>
      <tr>
        <!-- <td>{{ optionA }}</td>  -->
        <td>
          <div class="drawing-slider-container">
            <canvas
              ref="drawingCanvas"
              @mousedown="startDrawing"
              @mousemove="draw"
              @mouseup="endDrawing"
              @mouseout="endDrawing"
              class="drawing-canvas"
              width="1000"
              height="500"
            ></canvas>
            <button class="reset-btn" @click="resetCanvas">Reset</button>
          </div>
        </td>
        <!-- <td>{{ optionB }}</td> -->
      </tr>
    </table>
  </div>
</template>

<script>
export default {
  name: 'DrawingSliderComponent',
  props: {
    optionA: String,
    optionB: String,
    criterion: String,
    sliderIndex: Number,
  },
  data() {
    return {
      isDrawing: false,
      context: null,
      previousX: null,
      previousY: null,
      drawingData: [],  
      isCanvasLocked: false, 
      hasDrawnSomething: false, 
      hasDecreased: false, 
    };
  },
  mounted() {
    const canvas = this.$refs.drawingCanvas;
    this.context = canvas.getContext('2d');
  },
  methods: {
    getMousePos(event) {
      const rect = this.$refs.drawingCanvas.getBoundingClientRect();
      return {
        x: (event.clientX - rect.left) * (this.$refs.drawingCanvas.width / rect.width),
        y: (event.clientY - rect.top) * (this.$refs.drawingCanvas.height / rect.height)
      };
    },
    startDrawing(event) {
      if (this.isCanvasLocked) return; 
      this.isDrawing = true;
      const pos = this.getMousePos(event);
      this.context.beginPath();
      this.context.moveTo(pos.x, this.$refs.drawingCanvas.height);
      this.context.lineTo(pos.x, pos.y);
      this.context.stroke();
      
      this.previousX = pos.x;
      this.previousY = pos.y;

      this.hasDrawnSomething = true;

      this.drawingData.push({ x: pos.x, y: pos.y });
    },
    draw(event) {
      if (!this.isDrawing || this.isCanvasLocked) return;
      const pos = this.getMousePos(event);
      if (pos.x < this.previousX) return;

      if (pos.y > this.previousY) {
        this.hasDecreased = true;
      }

      if (this.hasDecreased && pos.y < this.previousY) {
        return; 
      } 
      this.context.lineTo(pos.x, pos.y);
      this.context.stroke();

      this.previousX = pos.x;
      this.previousY = pos.y;
      this.drawingData.push({ x: pos.x, y: pos.y });
    },
    endDrawing() {
      if (!this.isDrawing || this.isCanvasLocked) return;
      this.isDrawing = false;
      this.isCanvasLocked = true;
      
      const canvas = this.$refs.drawingCanvas;
      this.context.lineTo(this.previousX, canvas.height);
      this.context.stroke();

      this.emitDrawingData();
    },
    emitDrawingData() {
      this.$emit('drawingCompleted', { sliderIndex: this.sliderIndex, drawingData: this.drawingData });
      this.$emit('drawingStatusChanged', true); 
	},
    resetCanvas() {
      const canvas = this.$refs.drawingCanvas;
      this.context.clearRect(0, 0, canvas.width, canvas.height);
      this.drawingData = [];
      this.isCanvasLocked = false;
       this.hasDecreased = false; 
       this.hasDrawnSomething = false;
      this.$emit('drawingStatusChanged', false);
    }
  }
};
</script>

<style>
.drawing-slider-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}
.drawing-slider-container canvas {
  border: 1px solid black; /* Czarna kreska */
  width: 100%; /* Zmniejszenie szerokości kanwy do 100% kontenera */
  max-width: 1200px;
  height: 100%; 
}

button.reset-btn {
  background-color: red;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
}

</style>
