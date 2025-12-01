"""Unit tests for analysis models."""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from auth.models import User
from analysis.models import Analysis, ModelResult


class TestAnalysisModel:
    """Tests for the Analysis model."""

    def test_create_analysis(self, db_session):
        """Test creating a basic analysis."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="base64encodeddata",
            aggregate_confidence=0.75
        )
        db_session.add(analysis)
        db_session.commit()
        db_session.refresh(analysis)

        assert analysis.id is not None
        assert analysis.user_id == user.id
        assert analysis.filename == "test.jpg"
        assert analysis.image_data == "base64encodeddata"
        assert analysis.aggregate_confidence == 0.75
        assert isinstance(analysis.created_at, datetime)

    def test_analysis_user_required(self, db_session):
        """Test that user_id is required."""
        analysis = Analysis(
            filename="test.jpg",
            image_data="base64data",
            aggregate_confidence=0.5
        )
        db_session.add(analysis)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_analysis_filename_required(self, db_session):
        """Test that filename is required."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            image_data="base64data",
            aggregate_confidence=0.5
        )
        db_session.add(analysis)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_analysis_image_data_required(self, db_session):
        """Test that image_data is required."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            aggregate_confidence=0.5
        )
        db_session.add(analysis)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_analysis_aggregate_confidence_required(self, db_session):
        """Test that aggregate_confidence is required."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="base64data"
        )
        db_session.add(analysis)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_analysis_user_relationship(self, db_session):
        """Test the relationship between analysis and user."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="base64data",
            aggregate_confidence=0.8
        )
        db_session.add(analysis)
        db_session.commit()
        db_session.refresh(analysis)

        assert analysis.user is not None
        assert analysis.user.username == "testuser"

    def test_analysis_model_results_relationship(self, db_session):
        """Test that analysis has model_results relationship."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="base64data",
            aggregate_confidence=0.8
        )
        db_session.add(analysis)
        db_session.commit()
        db_session.refresh(analysis)

        assert hasattr(analysis, 'model_results')
        assert analysis.model_results == []

    def test_multiple_analyses_per_user(self, db_session):
        """Test creating multiple analyses for one user."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis1 = Analysis(
            user_id=user.id,
            filename="image1.jpg",
            image_data="data1",
            aggregate_confidence=0.7
        )
        analysis2 = Analysis(
            user_id=user.id,
            filename="image2.jpg",
            image_data="data2",
            aggregate_confidence=0.9
        )
        db_session.add_all([analysis1, analysis2])
        db_session.commit()

        user_analyses = db_session.query(Analysis).filter(Analysis.user_id == user.id).all()
        assert len(user_analyses) == 2
        assert {a.filename for a in user_analyses} == {"image1.jpg", "image2.jpg"}

    def test_analysis_cascade_delete(self, db_session):
        """Test that deleting analysis cascades to model results."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="data",
            aggregate_confidence=0.8
        )
        db_session.add(analysis)
        db_session.commit()

        result = ModelResult(
            analysis_id=analysis.id,
            model_name="CNNSpot",
            confidence=0.85
        )
        db_session.add(result)
        db_session.commit()

        # Verify the model result exists
        assert db_session.query(ModelResult).count() == 1

        # Delete the analysis
        db_session.delete(analysis)
        db_session.commit()

        # Verify the model result was cascade deleted
        assert db_session.query(ModelResult).count() == 0


class TestModelResultModel:
    """Tests for the ModelResult model."""

    def test_create_model_result(self, db_session):
        """Test creating a basic model result."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="data",
            aggregate_confidence=0.8
        )
        db_session.add(analysis)
        db_session.commit()

        result = ModelResult(
            analysis_id=analysis.id,
            model_name="CNNSpot",
            confidence=0.85
        )
        db_session.add(result)
        db_session.commit()
        db_session.refresh(result)

        assert result.id is not None
        assert result.analysis_id == analysis.id
        assert result.model_name == "CNNSpot"
        assert result.confidence == 0.85

    def test_model_result_analysis_required(self, db_session):
        """Test that analysis_id is required."""
        result = ModelResult(
            model_name="CNNSpot",
            confidence=0.85
        )
        db_session.add(result)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_model_result_model_name_required(self, db_session):
        """Test that model_name is required."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="data",
            aggregate_confidence=0.8
        )
        db_session.add(analysis)
        db_session.commit()

        result = ModelResult(
            analysis_id=analysis.id,
            confidence=0.85
        )
        db_session.add(result)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_model_result_confidence_required(self, db_session):
        """Test that confidence is required."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="data",
            aggregate_confidence=0.8
        )
        db_session.add(analysis)
        db_session.commit()

        result = ModelResult(
            analysis_id=analysis.id,
            model_name="CNNSpot"
        )
        db_session.add(result)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_model_result_analysis_relationship(self, db_session):
        """Test the relationship between model result and analysis."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="data",
            aggregate_confidence=0.8
        )
        db_session.add(analysis)
        db_session.commit()

        result = ModelResult(
            analysis_id=analysis.id,
            model_name="CNNSpot",
            confidence=0.85
        )
        db_session.add(result)
        db_session.commit()
        db_session.refresh(result)

        assert result.analysis is not None
        assert result.analysis.filename == "test.jpg"

    def test_multiple_model_results_per_analysis(self, db_session):
        """Test creating multiple model results for one analysis."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="data",
            aggregate_confidence=0.8
        )
        db_session.add(analysis)
        db_session.commit()

        result1 = ModelResult(
            analysis_id=analysis.id,
            model_name="CNNSpot",
            confidence=0.85
        )
        result2 = ModelResult(
            analysis_id=analysis.id,
            model_name="Nebula",
            confidence=0.75
        )
        result3 = ModelResult(
            analysis_id=analysis.id,
            model_name="OpenX8100",
            confidence=0.90
        )
        db_session.add_all([result1, result2, result3])
        db_session.commit()

        analysis_results = db_session.query(ModelResult).filter(
            ModelResult.analysis_id == analysis.id
        ).all()
        assert len(analysis_results) == 3
        assert {r.model_name for r in analysis_results} == {"CNNSpot", "Nebula", "OpenX8100"}

    def test_confidence_value_range(self, db_session):
        """Test that confidence can store various float values."""
        user = User(username="testuser", hashed_password="password123")
        db_session.add(user)
        db_session.commit()

        analysis = Analysis(
            user_id=user.id,
            filename="test.jpg",
            image_data="data",
            aggregate_confidence=0.5
        )
        db_session.add(analysis)
        db_session.commit()

        # Test extreme values
        result_low = ModelResult(
            analysis_id=analysis.id,
            model_name="LowConfidence",
            confidence=0.0
        )
        result_high = ModelResult(
            analysis_id=analysis.id,
            model_name="HighConfidence",
            confidence=1.0
        )
        result_mid = ModelResult(
            analysis_id=analysis.id,
            model_name="MidConfidence",
            confidence=0.5432
        )
        db_session.add_all([result_low, result_high, result_mid])
        db_session.commit()

        results = db_session.query(ModelResult).filter(
            ModelResult.analysis_id == analysis.id
        ).all()
        confidences = {r.model_name: r.confidence for r in results}

        assert confidences["LowConfidence"] == 0.0
        assert confidences["HighConfidence"] == 1.0
        assert abs(confidences["MidConfidence"] - 0.5432) < 0.0001
